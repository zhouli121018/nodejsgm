#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent.monkey

gevent.monkey.patch_all()

import email.utils
import gevent.backdoor
import gevent.pool
import gevent.queue
import hashlib
import json
import logging
import random
import re
import struct
import time
import urllib3
import zlib

import lib.common

lib.common.init_django_enev()

from django.core.exceptions import ObjectDoesNotExist
from django.db import InterfaceError, DatabaseError, connection
from django.db.models import Count
from django.db.transaction import atomic
from deliver.lib.model import email_pattern
from deliver.lib.models import deliver_model
from deliver.lib.utility import RetryQueue, address_domain
from apps.core.models import IpPool, ClusterIp, RouteRule, CustomerSetting
from apps.mail.models import get_mail_model, Settings
from lib.del_attach_from_msg import del_attach_from_msg

_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)s %(message)s'))

log = logging.getLogger('control')
log.addHandler(_handler)
log.setLevel(logging.DEBUG)

redis = lib.common.get_redis_cli()
http = urllib3.PoolManager(100, timeout=urllib3.Timeout(connect=10, read=300))


def pack_deliver(json_data, message):
    # body structure:
    #   json_size, compressed_size
    #   message_md5
    #   json_data
    #   compressed_data

    compressed_data = zlib.compress(message)
    md5 = hashlib.md5()
    md5.update(message)

    return struct.pack('!QQ', len(json_data), len(compressed_data)) + md5.digest() + json_data + compressed_data


def get_sender_from_message(message):
    try:
        message_object = email.message_from_string(message)
        return email.utils.parseaddr(message_object.get('from'))[1]
    except BaseException:
        return 'nobody@mailrelay.cn'


class Dispatcher(object):
    def __init__(self, cluster_ip):
        self.cluster_ip = cluster_ip
        self._queue = gevent.queue.Queue()
        self._pool = gevent.pool.Pool(20)
        self._last_success = time.time()
        self._last_fail = 0
        self._routine = gevent.spawn(self.run)

    def put(self, d, mail):
        self._queue.put((d, mail))

    def run(self):
        while True:
            d, mail = self._queue.get()
            self._pool.spawn(self.dispatch, d, mail)

    def dispatch(self, d, mail):
        message = mail.get_mail_content(is_del_attach=d['dispatch_data'][-1]['attachment_removed'])

        if len(message) == 0:
            d['state'] = 'fail_finished'
            (redis.pipeline()
             .lpush('control_dispatched', json.dumps(d))
             .lrem('control_dispatch_waiting', 0, d['mail_ident'])
             .execute())
            log.warning(u'dispatch: {} to {} skipped'.format(d['mail_ident'], self.cluster_ip))
            return

        if not re.match(email_pattern, d['sender']):
            d['sender'] = get_sender_from_message(message)

        j = json.dumps(deliver_model.dump({
            'mail_ident': d['mail_ident'],
            'sender': d['sender'],
            'receiver': d['receiver'],
            'deliver_ip': d['deliver_ip']
        }))
        deliver_model.load(json.loads(j))  # test if json_data is right
        body = pack_deliver(j, message)

        for port in (80, 88, 10001):
            url = 'http://{}:{}/deliver/'.format(self.cluster_ip, port)
            t0 = time.time()
            try:
                r = http.urlopen('PUT', url, body=body)
                t1 = time.time()
                if r.status == 200:
                    (redis.pipeline()
                     .lpush('control_dispatched', json.dumps(d))
                     .lrem('control_dispatch_waiting', 0, d['mail_ident'])
                     .execute())
                    log.info(u'dispatch: {} to {}, size={}, time={:.1f}'
                             .format(d['mail_ident'], self.cluster_ip, len(message), t1 - t0))
                    self._last_success = time.time()
                    return
                else:
                    log.warning(u'dispatch: {} to {} failed, size={}, time={:.1f}'
                                .format(d['mail_ident'], self.cluster_ip, len(message), t1 - t0))
            except BaseException:
                t1 = time.time()
                log.warning(u'dispatch: exception, {} to {}, size={}, time={:.1f}'
                            .format(d['mail_ident'], self.cluster_ip, len(message), t1 - t0),
                            exc_info=1)
            self._last_fail = time.time()
        else:
            gevent.sleep(60)
            (redis.pipeline()
             .lpush('relay_dispatch', d['mail_ident'])
             .lrem('control_dispatch_waiting', 0, d['mail_ident'])
             .execute())

    def state(self):
        if self._last_success >= self._last_fail:
            t = 0
        else:
            t = int(time.time() - self._last_success)
        return {
            'queue_size': self._queue.qsize(),
            'pool_size': len(self._pool),
            'exception_time': t
        }


def default_ip_pool(d, mail):
    """
    根据收件人域名或用户分配
    """

    rr = RouteRule.objects.filter(type='domain', domain=address_domain(d['receiver']), disabled=False).first()
    if rr is not None:
        return rr.ip_pool

    if mail.customer.ip_pool is None:
        free_pools = IpPool.objects.filter(type='auto').annotate(num_ip=Count('clusterip')).filter(
            num_ip__gt=0).annotate(num_customer=Count('customer', distinct=True)).order_by('num_customer')
        if len(free_pools) > 0:
            mail.customer.ip_pool = free_pools[0]
            mail.customer.save()

    return mail.customer.ip_pool


def remove_attachment(d):
    message = del_attach_from_msg(d['mail_ident'])
    redis.lpush('relay_sync', d['mail_ident'])
    log.info(u'remove_attachment: mail_ident={}'.format(d['mail_ident']))
    return message


def remove_attachment_test(d, mail, settings):
    """
    根据用户设置或默认设置,如果需要就进行网络附件处理
    """

    on = True
    threshold = settings.transfer_max_size * 1024 * 1024

    customer_setting = CustomerSetting.objects.filter(customer=mail.customer).first()
    if customer_setting is not None:
        on = customer_setting.bigmail
        if customer_setting.transfer_max_size > 0:
            threshold = customer_setting.transfer_max_size * 1024 * 1024

    if on and mail.size >= threshold:
        message = remove_attachment(d)
        d['dispatch_data'][-1]['attachment_removed'] = True
        d['dispatch_data'][-1]['real_mail_size'] = len(message)
    else:
        d['dispatch_data'][-1]['attachment_removed'] = False
        d['dispatch_data'][-1]['real_mail_size'] = mail.size


def init_dispatch_data(d, mail, settings):
    d['dispatch_data'] = [{'action': 'none'}]

    remove_attachment_test(d, mail, settings)

    if d['dispatch_data'][-1]['real_mail_size'] >= settings.big_email * 1024 * 1024:
        # 使用大邮件地址池
        d['dispatch_data'][-1]['ip_pool_type'] = 'big'
        ip_pool = settings.big_email_pool
    else:
        # 使用默认地址池
        d['dispatch_data'][-1]['ip_pool_type'] = 'default'
        ip_pool = default_ip_pool(d, mail)

    if ip_pool is None:
        return 'retry', None

    d['dispatch_data'][-1]['ip_pool_id'] = ip_pool.id

    all_ip = [(ip.ip, ip.cluster.ip)
              for ip in ip_pool.clusterip_set.filter(disabled=False)]

    if len(all_ip) == 0:
        return 'retry', None

    # 随机选择一个发送 IP
    deliver_ip, cluster_ip = random.choice(all_ip)
    d['deliver_ip'] = deliver_ip
    d['dispatch_data'][-1]['deliver_ip'] = deliver_ip
    d['dispatch_data'][-1]['cluster_ip'] = cluster_ip

    return 'ok', mail


def update_dispatch_data(d, mail, settings):
    d['dispatch_data'] = json.loads(mail.dispatch_data)

    if d['dispatch_data'][-1]['action'] == 'remove_attachment':
        message = remove_attachment(d)
        d['dispatch_data'][-1]['attachment_removed'] = True
        d['dispatch_data'][-1]['real_mail_size'] = len(message)

    if 'deliver_ip' in d['dispatch_data'][-1]:
        deliver_ip = d['dispatch_data'][-1]['deliver_ip']
        ip = ClusterIp.objects.filter(ip=deliver_ip, disabled=False).first()
        if ip is not None:
            d['deliver_ip'] = deliver_ip
            d['dispatch_data'][-1]['cluster_ip'] = ip.cluster.ip
            return 'ok', mail

    if d['dispatch_data'][-1]['action'] == 'allocate_default':
        d['dispatch_data'][-1]['ip_pool_type'] = 'default'
        ip_pool = default_ip_pool(d, mail)
        if ip_pool is None:
            return 'retry', None
        d['dispatch_data'][-1]['ip_pool_id'] = ip_pool.id
    else:
        ip_pool = IpPool.objects.filter(id=d['dispatch_data'][-1]['ip_pool_id']).first()
        if ip_pool is None:
            return 'retry', None

    all_ip = [(ip.ip, ip.cluster.ip)
              for ip in ip_pool.clusterip_set.filter(disabled=False)]

    if len(all_ip) == 0:
        return 'retry', None

    used_ip = {dd['deliver_ip'] for dd in d['dispatch_data'] if 'deliver_ip' in dd}
    unused_ip = [p for p in all_ip if p[0] not in used_ip]

    # 随机选择一个发送 IP
    deliver_ip, cluster_ip = random.choice(unused_ip if len(unused_ip) > 0 else all_ip)
    d['deliver_ip'] = deliver_ip
    d['dispatch_data'][-1]['deliver_ip'] = deliver_ip
    d['dispatch_data'][-1]['cluster_ip'] = cluster_ip

    return 'ok', mail


def load_mail(d):
    date, id = d['mail_ident'].split(',')[:2]
    for _ in xrange(5):
        try:
            with atomic():
                mail = get_mail_model(date).objects.get(id=id)
                settings = Settings.objects.get()

                try:
                    mail.customer
                except ObjectDoesNotExist:
                    return 'finish', None

                d['sender'] = mail.mail_from
                d['receiver'] = mail.mail_to

                if mail.dispatch_data is None:
                    return init_dispatch_data(d, mail, settings)
                else:
                    return update_dispatch_data(d, mail, settings)
        except (DatabaseError, InterfaceError) as e:
            # 如果报数据库异常，关闭连接，重新处理任务
            log.warning(u'load_mail: database exception', exc_info=1)
            connection.close()
        except BaseException as e:
            log.warning(u'load_mail: exception, mail_ident={}'.format(d['mail_ident']), exc_info=1)
        gevent.sleep(10)
    else:
        return 'retry', None


def put_one(mail_ident):
    d = {'mail_ident': mail_ident}
    cont, mail = load_mail(d)
    if cont == 'ok':
        if d['dispatch_data'][-1]['action'] == 'delay':
            delay_queue.put(d['dispatch_data'][-1]['next_time'], (d, mail))
        else:
            delay_queue.put(0, (d, mail))
    elif cont == 'retry':
        (redis.pipeline()
         .lpush('relay_dispatch', d['mail_ident'])
         .lrem('control_dispatch_waiting', 0, d['mail_ident'])
         .execute())
        log.warning(u'put_routine: error, mail_ident={}'.format(mail_ident))
    elif cont == 'finish':
        redis.lrem('control_dispatch_waiting', 0, d['mail_ident'])
        log.warning(u'put_routine: skipped, mail_ident={}'.format(mail_ident))
    else:
        assert 0


def put_routine():
    for mail_ident in reversed(redis.lrange('control_dispatch_waiting', 0, -1)):
        put_one(mail_ident)
    while True:
        mail_ident = redis.brpoplpush('relay_dispatch', 'control_dispatch_waiting')
        put_one(mail_ident)


def delay_routine():
    global dispatcher_dict

    dispatcher_dict = {}

    while True:
        d, mail = delay_queue.get()
        cluster_ip = d['dispatch_data'][-1]['cluster_ip']
        if cluster_ip not in dispatcher_dict:
            dispatcher_dict[cluster_ip] = Dispatcher(cluster_ip)
        dispatcher_dict[cluster_ip].put(d, mail)


def state_routine():
    while True:
        state_dict = {}
        for d in dispatcher_dict.values():
            s = d.state()
            state_dict[d.cluster_ip] = s
            if s['exception_time'] > 600:
                l = redis.lrange('control_dispatch_exception', 0, -1)
                if d.cluster_ip not in l:
                    redis.lpush('control_dispatch_exception', d.cluster_ip)
        redis.set('control_dispatch_state', json.dumps(state_dict))
        log.info(u'state_routine: update state')
        gevent.sleep(60)


def save(d):
    date, id = d['mail_ident'].split(',')[:2]
    while True:
        try:
            with atomic():
                mail = get_mail_model(date).objects.get(id=id)
                mail.dispatch_data = json.dumps(d['dispatch_data'])
                mail.deliver_ip = d['deliver_ip']
                if mail.state == 'dispatch':
                    if 'state' in d:
                        mail.state = d['state']
                    else:
                        mail.state = 'send'
                elif mail.state == 'retry':
                    if 'state' in d:
                        mail.state = d['state']
                    else:
                        mail.state = 'retry'
                else:
                    log.error(u'save: unexpected state, mail_ident={}, state={}'
                              .format(d['mail_ident'], mail.state))
                if d['dispatch_data'][-1]['attachment_removed']:
                    mail.is_del_attach = True
                mail.save(update_fields=['dispatch_data', 'deliver_ip', 'state', 'is_del_attach'])
                return
        except (DatabaseError, InterfaceError) as e:
            # 如果报数据库异常，关闭连接，重新处理任务
            log.warning(u'save: database exception', exc_info=1)
            connection.close()
        except BaseException as e:
            log.warning(u'save: exception, mail_ident={}'.format(d['mail_ident']), exc_info=1)
        gevent.sleep(10)


def sync_db():
    while redis.rpoplpush('control_dispatched_temp', 'control_dispatched') is not None:
        pass
    while True:
        j = redis.brpoplpush('control_dispatched', 'control_dispatched_temp')
        d = json.loads(j)
        save(d)
        redis.lrem('control_dispatched_temp', 0, j)
        log.info(u'sync_db: saved to postgres, mail_ident={}'.format(d['mail_ident']))


def main():
    global all_routine, delay_queue

    delay_queue = RetryQueue()

    all_routine = [
        gevent.spawn(gevent.backdoor.BackdoorServer(('localhost', 10003)).serve_forever),
        gevent.spawn(put_routine),
        gevent.spawn(delay_routine),
        gevent.spawn(state_routine),
        gevent.spawn(sync_db)
    ]
    gevent.joinall(all_routine)


if __name__ == '__main__':
    main()
