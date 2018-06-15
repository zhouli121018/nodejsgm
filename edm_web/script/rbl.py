# -*- coding: utf-8 -*-
#
'''
RBL 黑名单查询
'''
from gevent import monkey
monkey.patch_all()
import gevent
import gevent.pool

import json
import time
import redis
import traceback
from newlib.log import log
from newlib._signal import init_gevent_signal
from newlib import rblsearch, rbl_settings

redis_db = redis.Redis( host="127.0.0.1", port=6379 )
signal_stop = False

#####################################################
def _distribute(ip):
    log.info("search start IP: {}".format(ip))
    key = "rbl:search:domain"
    key2 = "rbl:search:domain:2"
    ret_key = "rbl:search:ret:{}".format(ip)
    hostname_key = "rbl:search:hostname"
    p = redis_db.pipeline()
    p.hincrby(ret_key, "score", 100)
    p.hset(ret_key, "created", time.time())
    p.expire(ret_key, 3600)
    p.lpush(hostname_key, ip)
    for ref in rbl_settings.RBL_SEARCH_DOMAINS:
        tagid, domain, answers, desc = ref
        p.lpush(key, json.dumps({
            "ip": ip,
            "tagid": tagid,
            "domain": domain,
            "answers": answers,
            "desc": desc,
        }))
    for ref in rbl_settings.RBL_SEARCH_DOMAINS2:
        tagid, domain, answers, desc = ref
        p.lpush(key2, json.dumps({
            "ip": ip,
            "tagid": tagid,
            "domain": domain,
            "answers": answers,
            "desc": desc,
        }))
    p.execute()

def distribute():
    key = "rbl:search:ip"
    while True:
        if signal_stop: break
        _, ip = redis_db.brpop(key)
        ret_key = "rbl:search:ret:{}".format(ip)
        if redis_db.exists(ret_key): continue
        try:
            _distribute(ip)
        except BaseException as e:
            redis_db.lpush(key, ip)
            log.error(traceback.format_exc())

#####################################################
def _search(d):
    j = json.loads(d)
    ip, tagid, domain, answers, desc = j["ip"], j["tagid"], j["domain"], j["answers"], j["desc"]
    log.info("search IP: {}, domain: {}".format(ip, domain))
    with gevent.Timeout(5):
        ret, T = rblsearch.RDnsQuery(ip=ip, domain=domain, answers=answers)
    status, msg = rblsearch.show_ret(ip, ret, T, desc)
    log.info("search msg: {}, domain: {}".format(msg, domain))
    filed = "domain:success:{}".format(tagid)
    key = "rbl:search:ret:{}".format(ip)
    p = redis_db.pipeline()
    p.hincrby(key, "searched", 1)
    if status:
        p.hincrby(key, "score", -10)
        filed = "domain:error:{}".format(tagid)
    p.hset(key, filed, msg)
    p.execute()
    inc = redis_db.hget(key, "searched")
    if int( inc ) >= 28:
        created = float(redis_db.hget(key, "created"))
        redis_db.hset(key, "total", time.time()-created)
        log.info("search finish IP: {}".format(ip))

def search():
    key = "rbl:search:domain"
    while True:
        if signal_stop: break
        _, d = redis_db.brpop(key)
        try:
            _search(d)
        except BaseException as e:
            redis_db.lpush(key, d)
            log.error(traceback.format_exc())

#####################################################
def hostname():
    key = "rbl:search:hostname"
    while True:
        if signal_stop: break
        _, ip = redis_db.brpop(key)
        try:
            ret = rblsearch.get_hostname(ip)
            ret_key = "rbl:search:ret:{}".format(ip)
            if not ret:
                redis_db.hincrby(ret_key, "score", -5)
                ret = "No Reverse DNS"
            redis_db.hset(ret_key, "domain", ret)
            log.info("search hostname: {}".format(ret))
        except BaseException as e:
            redis_db.lpush(key, ip)
            log.error(traceback.format_exc())

############################################################
# 信号量处理
def signal_handle(mode):
    log.info("catch signal: %s" % mode)
    global signal_stop
    signal_stop = True

def main():
    init_gevent_signal(signal_handle)
    gevent.joinall([
        gevent.spawn(distribute),
        gevent.spawn(hostname),

        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),

        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),

        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),
        gevent.spawn(search),

    ])

if __name__ == "__main__":
    log.info("program start...")
    main()
    log.info("program quit...")
