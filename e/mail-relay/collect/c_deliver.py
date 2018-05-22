#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent.monkey

gevent.monkey.patch_all()

import collections
import datetime
import gevent.backdoor
import gevent.pool
import gevent.queue
import gevent.socket
import json
import logging
import random
import smtplib
import time

import lib.common

lib.common.init_django_enev()

from django.db.transaction import atomic
from django.db import InterfaceError, DatabaseError, connection
from django.utils import timezone
from deliver.lib.utility import address_domain, decode_msg
from apps.core.models import Customer, CustomerSetting, ColCustomerDomain
from apps.collect_mail.models import get_mail_model, DeliverLog
from apps.mail.models import Settings
from lib.error_type import c_load_error_type_resource, c_get_error_type, c_retry_q

_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)s %(message)s'))

log = logging.getLogger('collect')
log.addHandler(_handler)
log.setLevel(logging.DEBUG)

redis = lib.common.get_redis_cli()

state_dict = {}
pool = gevent.pool.Pool(200)
result = gevent.queue.Queue(10)

settings = None
customer_table = None


class State(object):
    __slots__ = ['customer_id', 'domain', 'queue', 'task_number', 'fail_count', 'next_time', 'last_succeed']

    def __init__(self, customer_id, domain):
        self.customer_id = customer_id
        self.domain = domain
        self.queue = collections.deque()
        self.task_number = 0
        self.fail_count = 0
        self.next_time = 0
        self.last_succeed = time.time()


def send(host, port, use_ssl, sender, receiver, message):
    deliver_ip = None
    receive_ip = None
    try:
        with gevent.Timeout(1000):
            receive_ip = gevent.socket.gethostbyname(host)
            if receive_ip == '127.0.0.1':
                code, msg = -1, 'receive_ip error'
            else:
                if use_ssl:
                    s = smtplib.SMTP_SSL(host, port)
                else:
                    s = smtplib.SMTP(host, port)
                deliver_ip = s.sock.getsockname()[0]
                s.sendmail(sender, receiver, message)
                s.quit()
                code, msg = 250, 'ok'
    except smtplib.SMTPResponseException as e:
        code, msg = e.smtp_code, e.smtp_error
    except smtplib.SMTPRecipientsRefused as e:
        senderrs = e.recipients
        code, msg = senderrs[receiver]
    except gevent.Timeout:
        code, msg = -1, 'deliver timeout'
    except BaseException as e:
        log.warning(u'send: exception', exc_info=1)
        code, msg = -1, repr(e)
    return code, msg, deliver_ip, receive_ip


def deliver(d, mail):
    customer_id = d['customer_id']

    d['state'] = 'retry'
    try:
        if customer_id not in customer_table:
            # 用户被禁用
            return

        forward_list = [f for f in customer_table[customer_id]['forward'] if f['domain'] == d['domain']]
        if len(forward_list) == 0:
            # 没有转发地址
            return

        message = mail.get_mail_content()
        if not message:
            # 邮件不存在
            d['state'] = 'fail_finished'
            return

        for forward in forward_list:
            t0 = time.time()
            code, msg, deliver_ip, receive_ip = send(
                forward['address'], forward['port'], forward['use_ssl'], d['sender'], d['receiver'], message)
            msg = decode_msg(msg)

            if code == 250:
                error_type = 0
                d['state'] = 'finished'
            else:
                error_type = c_get_error_type(code, msg)
                if 500 <= code < 600 or not c_retry_q(error_type):
                    d['state'] = 'fail_finished'

            d['result'].append({
                'deliver_ip': deliver_ip,
                'deliver_time': datetime.datetime.now(),
                'receive_ip': receive_ip,
                'return_code': code,
                'return_message': msg,
                'error_type': error_type
            })

            t1 = time.time()
            log.info(u'deliver: deliver message, mail_ident={}, code={}, msg={}, address={}, state={}, time={:.1f}'
                     .format(d['mail_ident'], code, msg, forward['address'], d['state'], t1 - t0))

            if d['state'] != 'retry':
                return

    except BaseException as e:
        log.warning(u'deliver: exception, mail_ident={}'.format(d['mail_ident']), exc_info=1)

    finally:
        if d['state'] == 'retry' and (timezone.now() - mail.created).days >= settings.retry_days:
            d['state'] = 'fail_finished'
        if d['state'] == 'fail_finished' and customer_id in customer_table and customer_table[customer_id]['bounce']:
            d['state'] = 'bounce'
        result.put(d)


def load_customer_table():
    t = {}
    for c in Customer.objects.filter(gateway_status__in=('normal', 'expiring')):
        t[c.id] = {
            'id': c.id,
            'bounce': False,
            'forward': []
        }
    for cs in CustomerSetting.objects.filter(customer__gateway_status__in=('normal', 'expiring')):
        if cs.customer_id in t:
            t[cs.customer_id]['bounce'] = cs.c_bounce
    for cd in ColCustomerDomain.objects.filter(disabled=False, customer__gateway_status__in=('normal', 'expiring')):
        if cd.customer_id in t:
            t[cd.customer_id]['forward'].append({
                'domain': cd.domain,
                'address': cd.forward_address,
                'port': cd.port,
                'use_ssl': cd.is_ssl,
                'priority': cd.priority
            })
    for v in t.values():
        random.shuffle(v['forward'])
        v['forward'].sort(key=lambda x: x['priority'])
    return t


def load_resource():
    global settings, customer_table

    while True:
        try:
            c_load_error_type_resource()
            settings = Settings.objects.get()
            customer_table = load_customer_table()
            log.info(u'load_resource')
            return
        except BaseException as e:
            log.warning(u'load_resource: exception', exc_info=1)
            gevent.sleep(60)


def load_resource_routine():
    while True:
        gevent.sleep(60)
        load_resource()


def load_mail(mail_ident):
    date, id = mail_ident.split(',')[:2]

    while True:
        try:
            mail = get_mail_model(date).objects.get(id=id)
            d = {
                'customer_id': mail.customer_id,
                'domain': address_domain(mail.mail_to),
                'mail_ident': mail_ident,
                'sender': mail.mail_from,
                'receiver': mail.mail_to,
                'result': []
            }
            return d, mail
        except (DatabaseError, InterfaceError) as e:
            # 如果报数据库异常，关闭连接，重新处理任务
            log.warning(u'DatabaseError', exc_info=1)
            connection.close()
        except BaseException as e:
            log.warning(u'load_mail: exception', exc_info=1)
        gevent.sleep(10)


def put_one(mail_ident):
    d, mail = load_mail(mail_ident)
    key = d['customer_id'], d['domain']
    if key not in state_dict:
        state_dict[key] = State(*key)
    state_dict[key].queue.appendleft((d, mail))


def put_routine():
    for mail_ident in reversed(redis.lrange('collect_send_waiting', 0, -1)):
        put_one(mail_ident)
    while True:
        mail_ident = redis.brpoplpush('collect_send', 'collect_send_waiting')
        put_one(mail_ident)


def get_routine():
    while True:
        now = time.time()
        l = [s for s in state_dict.itervalues()
             if len(s.queue) > 0 and
             s.task_number < 5 and
             s.next_time < now]
        if len(l) > 0:
            s = random.choice(l)
            s.task_number += 1
            d, mail = s.queue.pop()
            pool.spawn(deliver, d, mail)
        else:
            gevent.sleep(1)


def save(d):
    date, id = d['mail_ident'].split(',')[:2]

    while True:
        try:
            with atomic():
                mail = get_mail_model(date).objects.get(id=id)
                if mail.state in ('send', 'retry'):
                    mail.state = d['state']
                else:
                    log.error(u'save: unexpected state, mail_ident={}, state={}'
                              .format(d['mail_ident'], mail.state))
                if len(d['result']) == 0:
                    mail.save(update_fields=['state'])
                else:
                    r = d['result'][-1]
                    mail.deliver_ip = r['deliver_ip']
                    mail.deliver_time = r['deliver_time']
                    mail.return_code = r['return_code']
                    mail.return_message = r['return_message']
                    mail.error_type = r['error_type']
                    mail.save(update_fields=['state', 'deliver_ip', 'deliver_time', 'return_code', 'return_message',
                                             'error_type'])
                    for r in d['result']:
                        dl = DeliverLog(
                            date=date,
                            mail_id=id,
                            deliver_ip=r['deliver_ip'],
                            deliver_time=r['deliver_time'],
                            receive_ip=r['receive_ip'],
                            return_code=r['return_code'],
                            return_message=r['return_message'],
                        )
                        dl.save()
            return
        except (DatabaseError, InterfaceError) as e:
            # 如果报数据库异常，关闭连接，重新处理任务
            log.warning(u'DatabaseError', exc_info=1)
            connection.close()
        except BaseException as e:
            log.warning(u'save: exception', exc_info=1)
        gevent.sleep(10)


def result_routine():
    while True:
        d = result.get()
        now = time.time()

        key = d['customer_id'], d['domain']
        s = state_dict[key]
        s.task_number -= 1
        if d['state'] == 'retry':
            s.fail_count += 1
            s.next_time = now + 10 * min(10, s.fail_count)
        else:
            s.fail_count = 0
            s.next_time = 0
            s.last_succeed = now

        if s.fail_count > 30 and now - s.last_succeed > 1800:
            s.last_succeed = now
            a = '{},{}'.format(d['customer_id'], d['domain'])
            l = redis.lrange('collect_deliver_exception', 0, -1)
            if a not in l:
                redis.lpush('collect_deliver_exception', a)

        save(d)

        if d['state'] == 'retry':
            (redis.pipeline()
             .lpush('collect_send', d['mail_ident'])
             .lrem('collect_send_waiting', 0, d['mail_ident'])
             .execute())
        elif d['state'] == 'bounce':
            (redis.pipeline()
             .lpush('collect_bounce', json.dumps(d, cls=lib.common.ComplexEncoder))
             .lrem('collect_send_waiting', 0, d['mail_ident'])
             .execute())
        else:
            redis.lrem('collect_send_waiting', 0, d['mail_ident'])

        log.info(u'result_routine: saved to postgres, mail_ident={}'.format(d['mail_ident']))


def main():
    global all_routine

    load_resource()
    all_routine = [
        gevent.spawn(gevent.backdoor.BackdoorServer(('localhost', 10004)).serve_forever),
        gevent.spawn(load_resource_routine),
        gevent.spawn(put_routine),
        gevent.spawn(get_routine),
        gevent.spawn(result_routine)
    ]
    gevent.joinall(all_routine)


if __name__ == '__main__':
    main()
