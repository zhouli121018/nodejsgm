#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent.monkey

gevent.monkey.patch_all()

import datetime
import gevent.pool
import json
import time
import urllib3

from lib.core import config, log, get_redis_cli, del_message
from lib.models import log_list_model

redis_cli = get_redis_cli()
http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=10, read=300))


##################################################
def parse_one(d):
    result = [
        {
            'deliver_time': datetime.datetime.fromtimestamp(r['deliver_time']),
            'mx_record': r['mx_record'],
            'receive_ip': r['receive_ip'],
            'return_code': r['return_code'],
            'return_message': r['return_message']
        }
        for r in d['result']
        ]
    return {
        'mail_ident': d['mail_ident'],
        'sender': d['sender'],
        'receiver': d['receiver'],
        'deliver_ip': d['deliver_ip'],
        'result': result
    }


def parse_log(l):
    return map(parse_one, l)


def put_log(l):
    url = 'http://{}:{}/log/'.format(config['task']['host'], config['task']['port'])

    body = json.dumps(log_list_model.dump(parse_log(l)))

    # test if json_data is right
    log_list_model.load(json.loads(body))

    while True:
        try:
            r = http.urlopen('PUT', url, body=body)
            if r.status == 200:
                return
            else:
                log.warning(u'put_log: fail, response={}'.format((r.status, r.reason)))
        except BaseException as e:
            log.warning(u'put_log: error', exc_info=1)
        gevent.sleep(60)


##################################################
def available_key():
    """
    获取一个空的 list 的 key
    """

    i = 0
    while True:
        key = 'logging_{}'.format(i)
        if not redis_cli.exists(key):
            return key
        i += 1


def collect(max_count, wait_time):
    """
    收集数据到一个 list，直到 list 满或超时，返回对应的 key
    """

    key = available_key()
    end_time = time.time() + wait_time
    while True:
        left_time = int(end_time - time.time())
        if left_time > 0 and redis_cli.brpoplpush('delivered', key, left_time) is not None:
            if redis_cli.llen(key) >= max_count:
                break
        else:
            if redis_cli.llen(key) > 0 and len(pool) == 0:
                break
            else:
                end_time = time.time() + wait_time
    return key


##################################################
def work(key):
    """
    将 key 对应的 list 的数据上传的中控服务器，成功后删除 list 和对应文件
    """

    ident_list = redis_cli.lrange(key, 0, -1)
    l = map(json.loads, redis_cli.hmget('detail', ident_list))

    log.info(u'begin save: key={}, len={}'.format(key, len(l)))

    put_log(l)

    (redis_cli.pipeline()
     .delete(key)
     .hdel('detail', *ident_list)
     .execute())

    for r in l:
        del_message(r['mail_ident'])

    log.info(u'end save: key={}'.format(key))


##################################################
def main():
    global pool
    pool = gevent.pool.Pool(5)
    for k in redis_cli.keys('logging_*'):
        pool.spawn(work, k)
    while True:
        k = collect(200, 10)
        pool.spawn(work, k)


if __name__ == '__main__':
    main()
