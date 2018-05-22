#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent.monkey

gevent.monkey.patch_all()

import patch_multipartparser

import datetime
import flask
import gevent.wsgi
import hashlib
import json
import logging
import re
import struct
import time
import zlib

import lib.common

lib.common.init_cfg_default()
lib.common.init_django_enev()

from django.core.exceptions import ObjectDoesNotExist
from django.db import InterfaceError, DatabaseError, connection
from django.db.transaction import atomic
from django.db.models import Q
from deliver.lib.models import log_model, log_list_model
from apps.core.models import IpPool, RouteRule, CustomerSetting, CustomerLocalizedSetting
from apps.localized_mail.models import LocalizedMail
from apps.mail.models import get_mail_model, DeliverLog, Settings
from apps.collect_mail.models import get_mail_model as c_get_mail_model
from lib.error_type import load_error_type_resource, get_error_type
from redis_cache import get_redis_connection

try:
    from check import check_edm_mail
except:
    pass

config = {
    'server_address': lib.common.cfgDefault.get('log', 'server_address'),
    'server_port': lib.common.cfgDefault.getint('log', 'server_port'),
    'review_help_mode': lib.common.cfgDefault.get('review_help', 'mode'),
    'review_help_token': lib.common.cfgDefault.get('review_help', 'token'),
    'review_help_server_ip': lib.common.cfgDefault.get('review_help', 'server_ip'),
    'review_help_server_port': lib.common.cfgDefault.getint('review_help', 'server_port')
}

_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)s %(message)s'))

log = logging.getLogger('control')
log.addHandler(_handler)
log.setLevel(logging.DEBUG)

redis = lib.common.get_redis_cli()
app = flask.Flask(__name__)


@app.route('/log/', methods=['put'])
def log_():
    l = log_list_model.load(json.loads(flask.request.data))
    pipe = redis.pipeline()
    for d in l:
        pipe.lpush('control_log', json.dumps(log_model.dump(d)))
    pipe.execute()
    log.info(u'log_: saved to redis, len={}'.format(len(l)))
    return ''


@app.route('/retry_state/')
def retry_state():
    j = json.loads(flask.request.data)
    error_type = get_error_type(j['return_code'], j['return_message'])
    s = error_type not in (2, 4, 5, 6, 7, 9)
    return json.dumps({'retry_state': s})


def unpack_message(body):
    # body structure:
    #   json_size, compressed_size
    #   message_md5
    #   json_data
    #   compressed_data

    json_size, compressed_size = struct.unpack('!QQ', body[:16])
    json_data = body[32:32 + json_size]
    compressed_data = body[32 + json_size:]
    assert len(compressed_data) == compressed_size
    message = zlib.decompress(compressed_data)
    md5 = hashlib.md5()
    md5.update(message)
    assert md5.digest() == body[16:32]

    return json_data, message


def review_help():
    remote_ip = flask.request.remote_addr

    json_data, message = unpack_message(flask.request.data)
    d = json.loads(json_data)

    setting = CustomerLocalizedSetting.objects.filter(token=d['token'], ip=remote_ip).first()
    if setting is None:
        log.info(u'review_help: forbidden, ip={}, key={},{},{}'
                 .format(remote_ip, d['origin'], d['date'], d['mail_id']))
        flask.abort(403)

    mail = LocalizedMail(
        customer=setting.customer,
        origin=d['origin'],
        created_date=datetime.datetime.strptime(d['date'], '%Y%m%d'),
        mail_id=d['mail_id'],
        mail_from=d['sender'],
        mail_to=d['receiver'],
        subject=d['subject'],
        size=d['message_size'],
        check_result=d['check_result'],
        check_message=d['check_message']
    )
    mail.save()

    with open(mail.get_mail_path(), 'wb') as f:
        f.write(message)

    log.info(u'review_help: ip={}, key={},{},{}'.format(remote_ip, d['origin'], d['date'], d['mail_id']))

    return ''


def review_result():
    remote_ip = flask.request.remote_addr
    if remote_ip != config['review_help_server_ip']:
        log.warning(u'review_result: forbidden, ip={}'.format(remote_ip))
        flask.abort(403)

    d = json.loads(flask.request.data)
    if d['origin'] == 'relay':
        mails = (get_mail_model(d['date']).objects.filter(state='review')
                 .filter(Q(id=d['mail_id']) | Q(mail_id=d['mail_id'])))
        if len(mails) == 0:
            log.info(u'review_result: skip, ip={}, key={},{},{}'
                     .format(remote_ip, d['origin'], d['date'], d['mail_id']))
        elif d['review_result'] == 'pass':
            keys = [m.get_mail_filename() for m in mails]
            mails.update(state='dispatch', review_result=d['review_result'], review_time=datetime.datetime.now())
            map(lambda key: redis.lpush('relay_dispatch', key), set(keys))
            log.info(u'review_result: pass, ip={}, key={},{},{}'
                     .format(remote_ip, d['origin'], d['date'], d['mail_id']))
        elif d['review_result'] == 'reject':
            mails.update(state='reject', review_result=d['review_result'], review_time=datetime.datetime.now())
            log.info(u'review_result: reject, ip={}, key={},{},{}'
                     .format(remote_ip, d['origin'], d['date'], d['mail_id']))
        else:
            assert 0

    elif d['origin'] == 'collect':
        mails = (c_get_mail_model(d['date']).objects.filter(state='review')
                 .filter(Q(id=d['mail_id']) | Q(mail_id=d['mail_id'])))
        if len(mails) == 0:
            log.info(u'review_result: skip, ip={}, key={},{},{}'
                     .format(remote_ip, d['origin'], d['date'], d['mail_id']))
        elif d['review_result'] == 'pass':
            keys = [m.get_mail_filename() for m in mails]
            mails.update(state='send', review_result=d['review_result'], review_time=datetime.datetime.now())
            map(lambda key: redis.lpush('collect_send', key), set(keys))
            log.info(u'review_result: pass, ip={}, key={},{},{}'
                     .format(remote_ip, d['origin'], d['date'], d['mail_id']))
        elif d['review_result'] == 'reject':
            mails.update(state='reject', review_result=d['review_result'], review_time=datetime.datetime.now())
            log.info(u'review_result: reject, ip={}, key={},{},{}'
                     .format(remote_ip, d['origin'], d['date'], d['mail_id']))
        else:
            assert 0

    else:
        assert 0

    return ''


if config['review_help_mode'] == 'server':
    app.route('/review_help/', methods=['put'])(review_help)
elif config['review_help_mode'] == 'client':
    app.route('/review_result/', methods=['put'])(review_result)


@app.route('/check/', methods=['post'])
def check():
    sender = flask.request.form.get('sender')
    receiver = flask.request.form.get('receiver')
    message = flask.request.form.get('message')
    mail = {
        'sender': sender,
        'receiver': [receiver],
        'message': message
    }
    r = check_edm_mail(mail)
    return json.dumps(r)


def load_resource_routine():
    while True:
        gevent.sleep(60)
        try:
            load_error_type_resource()
            log.info(u'load_error_type_resource')
        except BaseException as e:
            log.warning(u'load_resource_routine: exception', exc_info=1)


def match_route_rule(return_message):
    for rr in RouteRule.objects.filter(type='keyword', disabled=False):
        if re.search(rr.keyword, return_message, re.IGNORECASE):
            return rr.ip_pool


def retry_action(d, keys, pairs):
    new = {}
    for k in keys:
        new[k] = d['dispatch_data'][-1][k]
    for k, v in pairs:
        new[k] = v
    d['dispatch_data'].append(new)
    d['state'] = 'retry'
    return lambda redis_other: redis_other.lpush('relay_dispatch', d['mail_ident'])


def bounce_action(j, d):
    d['state'] = 'bounce'
    return lambda redis_other: redis_other.lpush('control_bounce', j)


def determine(j, d, mail):
    d['dispatch_data'] = json.loads(mail.dispatch_data)

    r = d['result'][-1]
    if r['return_code'] == 250:
        d['error_type'] = 0
    else:
        d['error_type'] = get_error_type(r['return_code'], u'\n'.join([r1['return_message'] for r1 in d['result']]))

    try:
        mail.customer
    except ObjectDoesNotExist:
        d['state'] = 'fail_finished'
        return

    if r['return_code'] == 250:  # 成功
        d['state'] = 'finished'
        return

    customer_setting = CustomerSetting.objects.filter(customer=mail.customer).first()
    if ((d['error_type'] == 4
         or (d['error_type'] == 8 and d['dispatch_data'][-1]['ip_pool_type'] != 'big'))
        and (customer_setting is None or customer_setting.bigmail)):  # 超大满 或 发送超时
        if d['dispatch_data'][-1]['attachment_removed']:  # 已经进行了网络附件处理
            return bounce_action(j, d)
        else:  # 还没有进行网络附件处理
            return retry_action(d,
                                ('attachment_removed', 'ip_pool_type', 'ip_pool_id', 'deliver_ip'),
                                (('action', 'remove_attachment'),))

    if d['error_type'] in (2, 4, 5, 6, 7):  # 所有不重试错误类型
        return bounce_action(j, d)

    if d['error_type'] == 9:  # 灰名单错误类型
        i = len(d['dispatch_data']) - 1
        delay_count = 0
        while i >= 0 and d['dispatch_data'][i]['action'] == 'delay':
            i -= 1
            delay_count += 1
        if delay_count < 3:
            # 最多重试3次，间隔分别为5、10、15分钟
            return retry_action(d,
                                ('attachment_removed', 'ip_pool_type', 'ip_pool_id', 'deliver_ip'),
                                (('action', 'delay'),
                                 ('next_time', time.time() + (delay_count + 1) * 300)))

    if d['dispatch_data'][-1]['ip_pool_type'] in ('big', 'default'):  # (当前为大邮件地址池 或 默认地址池) 且 匹配线路不通地址池
        ip_pool = match_route_rule(r['return_message'])
        if ip_pool is not None:
            return retry_action(d,
                                ('attachment_removed',),
                                (('action', 'none'),
                                 ('ip_pool_type', 'unreachable'),
                                 ('ip_pool_id', ip_pool.id)))

    if d['dispatch_data'][-1]['ip_pool_type'] == 'big':  # 当前为大邮件地址池
        return retry_action(d,
                            ('attachment_removed',),
                            (('action', 'allocate_default'),))

    settings = Settings.objects.get()
    if settings.retry_mode == 'multi_ip':  # (多 IP 模式) 且 (当前地址池还有没使用的 IP)
        ip_pool = IpPool.objects.filter(id=d['dispatch_data'][-1]['ip_pool_id']).first()
        if ip_pool is not None:
            all_ip = {ip.ip for ip in ip_pool.clusterip_set.filter(disabled=False)}
            used_ip = {dd['deliver_ip'] for dd in d['dispatch_data'] if 'deliver_ip' in dd}
            if len(all_ip - used_ip) > 0:
                return retry_action(d,
                                    ('attachment_removed', 'ip_pool_type', 'ip_pool_id'),
                                    (('action', 'none'),))

    return bounce_action(j, d)


def save(d, mail):
    mail.dispatch_data = json.dumps(d['dispatch_data'])
    r = d['result'][-1]
    mail.deliver_time = r['deliver_time']
    mail.return_code = r['return_code']
    mail.return_message = r['return_message']
    mail.error_type = d['error_type']
    if mail.state not in ('send', 'retry'):
        log.error(u'save: unexpected state, mail_ident={}, state={}'.format(d['mail_ident'], mail.state))
    mail.state = d['state']
    mail.save(update_fields=['dispatch_data', 'deliver_time', 'return_code', 'return_message', 'error_type', 'state'])

    mail._do_error_type()

    date, id = d['mail_ident'].split(',')[:2]
    for r in d['result']:
        dl = DeliverLog(
            date=date,
            mail_id=id,
            deliver_ip=d['deliver_ip'],
            deliver_time=r['deliver_time'],
            mx_record=r['mx_record'],
            receive_ip=r['receive_ip'],
            return_code=r['return_code'],
            return_message=r['return_message'],
        )
        dl.save()


def determine_and_save(j, d):
    date, id = d['mail_ident'].split(',')[:2]
    while True:
        try:
            with atomic():
                mail = get_mail_model(date).objects.get(id=id)
                action = determine(j, d, mail)
                save(d, mail)
            if action is not None:
                action(get_redis_connection(mail.server_id))
            return True
        except (DatabaseError, InterfaceError) as e:
            # 如果报数据库异常，关闭连接，重新处理任务
            log.warning(u'determine_and_save: database exception', exc_info=1)
            connection.close()
        except BaseException as e:
            log.warning(u'determine_and_save: exception, mail_ident={}'.format(d['mail_ident']), exc_info=1)
        gevent.sleep(1)
        return False


def sync_db():
    while redis.rpoplpush('control_log_temp', 'control_log') is not None:
        pass
    while True:
        j = redis.brpoplpush('control_log', 'control_log_temp')
        d = log_model.load(json.loads(j))
        if determine_and_save(j, d):
            redis.lrem('control_log_temp', 0, j)
            log.info(u'sync_db: saved to postgres, mail_ident={}'.format(d['mail_ident']))
        else:
            (redis.pipeline()
             .lpush('control_log', j)
             .lrem('control_log_temp', 0, j)
             .execute())


def main():
    load_error_type_resource()
    server = gevent.wsgi.WSGIServer((config['server_address'], config['server_port']), app)
    gevent.joinall([
        gevent.spawn(server.serve_forever),
        gevent.spawn(load_resource_routine),
        gevent.spawn(sync_db)
    ])


if __name__ == '__main__':
    main()
