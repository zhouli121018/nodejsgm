#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent.monkey

gevent.monkey.patch_all()

import gevent.pool
import hashlib
import json
import logging
import struct
import time
import urllib3
import zlib

import lib.common

lib.common.init_cfg_default()
lib.common.init_django_enev()

from django.db import InterfaceError, DatabaseError, connection
from apps.core.models import CustomerLocalizedSetting
from apps.localized_mail.models import LocalizedMail
from apps.mail.models import get_mail_model
from apps.collect_mail.models import get_mail_model as c_get_mail_model

config = {
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
http = urllib3.PoolManager(100, timeout=urllib3.Timeout(connect=10, read=300))


##################################################
def pack_message(json_data, message):
    # body structure:
    #   json_size, compressed_size
    #   message_md5
    #   json_data
    #   compressed_data

    compressed_data = zlib.compress(message)
    md5 = hashlib.md5()
    md5.update(message)

    return struct.pack('!QQ', len(json_data), len(compressed_data)) + md5.digest() + json_data + compressed_data


def put_review_help(key, d, mail):
    message = mail.get_mail_content()
    j = json.dumps(d)

    url = 'http://{}:{}/review_help/'.format(config['review_help_server_ip'], config['review_help_server_port'])
    body = pack_message(j, message)

    while True:
        t0 = time.time()
        try:
            r = http.urlopen('PUT', url, body=body)
            t1 = time.time()
            if r.status == 200:
                redis.lrem('control_review_help_temp', 0, key)
                log.info(u'put_review_help: key={}, size={}, time={:.1f}'
                         .format(key, len(message), t1 - t0))
                return
            else:
                log.warning(u'put_review_help: failed, key={}, size={}, time={:.1f}'
                            .format(key, len(message), t1 - t0))
        except BaseException:
            t1 = time.time()
            log.warning(u'put_review_help: exception, key={}, size={}, time={:.1f}'
                        .format(key, len(message), t1 - t0),
                        exc_info=1)
        gevent.sleep(60)


def load_mail(key, origin, date, mail_id):
    while True:
        try:
            if origin == 'relay':
                return get_mail_model(date).objects.get(id=mail_id)
            elif origin == 'collect':
                return c_get_mail_model(date).objects.get(id=mail_id)
            else:
                assert 0
        except (DatabaseError, InterfaceError) as e:
            # 如果报数据库异常，关闭连接，重新处理任务
            log.warning(u'load_mail: database exception, key={}'.format(key), exc_info=1)
            connection.close()
        except BaseException as e:
            log.warning(u'load_mail: exception, key={}'.format(key), exc_info=1)
        gevent.sleep(10)


def put_review_help_routine():
    pool = gevent.pool.Pool(10)
    while redis.rpoplpush('control_review_help_temp', 'control_review_help') is not None:
        pass
    while True:
        key = redis.brpoplpush('control_review_help', 'control_review_help_temp')
        origin, date, mail_id = key.split(',')
        mail = load_mail(key, origin, date, mail_id)
        d = {
            'origin': origin,
            'date': date,
            'mail_id': mail_id,
            'token': config['review_help_token'],
            'sender': mail.mail_from,
            'receiver': mail.mail_to,
            'subject': mail.subject,
            'message_size': mail.size,
            'check_result': mail.check_result,
            'check_message': mail.check_message
        }
        pool.spawn(put_review_help, key, d, mail)


##################################################
def put_review_result(id, mail, setting):
    if mail.state == 'passing':
        result = 'pass'
    elif mail.state == 'rejecting':
        result = 'reject'
    else:
        redis.lrem('control_review_result_temp', 0, id)
        log.info(u'put_review_result: skip, id={}'.format(id))
        return

    j = json.dumps({
        'origin': mail.origin,
        'date': mail.created_date.strftime('%Y%m%d'),
        'mail_id': mail.mail_id,
        'mail_ident': mail.mail_id,
        'review_result': result
    })

    while True:
        try:
            url = 'http://{}:{}/review_result/'.format(setting.ip, setting.port)
            r = http.urlopen('PUT', url, body=j)
            if r.status == 200:
                (redis.pipeline()
                 .lpush('control_review_result_sync', id)
                 .lrem('control_review_result_temp', 0, id)
                 .execute())
                log.info(u'put_review_result: id={}'.format(id))
                return
            else:
                log.warning(u'put_review_result: failed, id={}'.format(id))
        except BaseException:
            log.warning(u'put_review_result: exception, id={}'.format(id), exc_info=1)
        gevent.sleep(60)


def load_localized_mail(id):
    while True:
        try:
            mail = LocalizedMail.objects.get(id=id)
            setting = CustomerLocalizedSetting.objects.get(customer=mail.customer)
            return mail, setting
        except (DatabaseError, InterfaceError) as e:
            # 如果报数据库异常，关闭连接，重新处理任务
            log.warning(u'load_localized_mail: database exception, id={}'.format(id), exc_info=1)
            connection.close()
        except BaseException as e:
            log.warning(u'load_localized_mail: exception, id={}'.format(id), exc_info=1)
        gevent.sleep(10)


def put_review_result_routine():
    pool = gevent.pool.Pool(10)
    while redis.rpoplpush('control_review_result_temp', 'control_review_result') is not None:
        pass
    while True:
        id = redis.brpoplpush('control_review_result', 'control_review_result_temp')
        mail, setting = load_localized_mail(id)
        pool.spawn(put_review_result, id, mail, setting)


def save(id):
    while True:
        try:
            mail = LocalizedMail.objects.get(id=id)
            if mail.state == 'passing':
                mail.state = 'pass'
                mail.save(update_fields=['state'])
            elif mail.state == 'rejecting':
                mail.state = 'reject'
                mail.save(update_fields=['state'])
            else:
                log.warning(u'save: unexpected state, id={}, state={}'.format(id, mail.state))
            return
        except (DatabaseError, InterfaceError) as e:
            # 如果报数据库异常，关闭连接，重新处理任务
            log.warning(u'save: database exception, id={}'.format(id), exc_info=1)
            connection.close()
        except BaseException as e:
            log.warning(u'save: exception, id={}'.format(id), exc_info=1)
        gevent.sleep(10)


def sync_db():
    while redis.rpoplpush('control_review_result_sync_temp', 'control_review_result_sync') is not None:
        pass
    while True:
        id = redis.brpoplpush('control_review_result_sync', 'control_review_result_sync_temp')
        save(id)
        redis.lrem('control_review_result_sync_temp', 0, id)
        log.info(u'sync_db: saved to postgres, id={}'.format(id))


##################################################
def main():
    if config['review_help_mode'] == 'client':
        gevent.joinall([
            gevent.spawn(put_review_help_routine)
        ])
    elif config['review_help_mode'] == 'server':
        gevent.joinall([
            gevent.spawn(put_review_result_routine),
            gevent.spawn(sync_db)
        ])


if __name__ == '__main__':
    main()
