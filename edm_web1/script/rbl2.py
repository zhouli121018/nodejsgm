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
from newlib import rblsearch2

redis_db = redis.Redis( host="127.0.0.1", port=6379 )
signal_stop = False

#####################################################
def _search(d):
    j = json.loads(d)
    ip, tagid, domain, answers, desc = j["ip"], j["tagid"], j["domain"], j["answers"], j["desc"]
    log.info("search2 IP: {}, domain: {}".format(ip, domain))
    with gevent.Timeout(2):
        ret, T = rblsearch2.RDnsQuery(ip=ip, domain=domain, answers=answers)
    status, msg = rblsearch2.show_ret(ip, ret, T, desc)
    log.info("search2 msg: {}, domain: {}".format(msg, domain))
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
        log.info("search2 finish IP: {}".format(ip))

def search():
    key = "rbl:search:domain:2"
    while True:
        if signal_stop: break
        _, d = redis_db.brpop(key)
        try:
            _search(d)
        except BaseException as e:
            redis_db.lpush(key, d)
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
