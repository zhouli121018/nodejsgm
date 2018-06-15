# -*- coding: utf-8 -*-
#
from gevent import monkey
monkey.patch_all()

import gevent
import gevent.pool
import json
import datetime
import time
import traceback
from libs import DB
from libs.log import loger
from libs._signal import init_gevent_signal
from libs.tools import validateQQ, validateEmail

from libs.mongo import remote_mongo, local_mongo

redis = DB.redis_db
log = loger("Test")
signal_stop=False
LIMIT = 20000
REDIS_KEY = "cce7e4f11fc518f7fff230079ab0edc9"

############################################################
def init():
    key = "mongo:cce7e4f11fc518f7fff230079ab0edc9:init"
    nextkey = "mongo:cce7e4f11fc518f7fff230079ab0edc9:nextlimit"
    addrkey = "mongo:cce7e4f11fc518f7fff230079ab0edc9:addr"
    skip = redis.get(nextkey)
    skip = skip and int(skip) or 0
    p = redis.pipeline()
    p.lpush(key, skip)
    p.expire(key, 15*24*60*60)
    p.set(nextkey, skip)
    p.expire(nextkey, 15*24*60*60)
    p.lpush(addrkey, "1@qq.com")
    p.expire(addrkey, 15*24*60*60)
    p.execute()

############################################################
def init_router():
    key = "mongo:cce7e4f11fc518f7fff230079ab0edc9:init"
    nextkey = "mongo:cce7e4f11fc518f7fff230079ab0edc9:nextlimit"
    skip = redis.get(nextkey)
    skip = skip and int(skip) or 0
    while True:
        if signal_stop: break
        if skip>=35000000:
            gevent.sleep(3600)
            log.error("Iinit end...")
            log.error("Iinit end...")
            log.error("Iinit end...")
            log.error("Iinit end...")
            continue
        skip += LIMIT
        p = redis.pipeline()
        p.lpush(key, skip)
        p.set(nextkey, skip)
        p.execute()
        gevent.sleep(5)

############################################################
def _fetchmongo(db, skip):
    res = db.find().skip(skip).limit(LIMIT)
    if not res: return
    log.info("--------------------------------------start skip: {}".format(skip))
    addrkey = "mongo:cce7e4f11fc518f7fff230079ab0edc9:addr"
    for i in res:
        redis.lpush(addrkey, i["addr"])

def fetchmongo():
    key = "mongo:cce7e4f11fc518f7fff230079ab0edc9:init"
    db = remote_mongo['mm-mc'].badmail
    while True:
        if signal_stop: break
        _, skip = redis.brpop(key)
        skip = int(skip)
        try:
            _fetchmongo(db, skip)
        except BaseException as e:
            log.error(traceback.format_exc())
            redis.lpush(key, skip)
            db = remote_mongo['mm-mc'].badmail

############################################################
def _localsave(db, db2, addr):
    if not validateEmail(addr): return
    if validateQQ(addr):
        if not db2.find_one({ "addr": addr }):
            log.info("start2 addr: {}".format(addr))
            db2.insert({ 'addr': addr, "created": int(time.time()) })
    else:
        if not db.find_one({ "addr": addr }):
            log.info("start addr: {}".format(addr))
            db.insert({ 'addr': addr, "created": int(time.time()) })
    return
    log.info("start addr: {}".format(addr))
    criteria = { "addr": addr }
    objNew = { "$set": {'addr': addr, 'created': int(time.time()) } }
    # 跟新时间 或者插入新纪录
    if validateQQ(addr):
        db2.update(criteria, objNew, True, False)
    else:
        db.update(criteria, objNew, True, False)


def localsave():
    key = "mongo:cce7e4f11fc518f7fff230079ab0edc9:addr"
    db = local_mongo['mm-mc'].badmail
    db2 = local_mongo['mm-mc'].invalidqq
    while True:
        if signal_stop: break
        _, addr = redis.brpop(key)
        try:
            _localsave(db, db2, addr)
        except BaseException as e:
            log.error(traceback.format_exc())
            redis.lpush(key, addr)
            db = local_mongo['mm-mc'].badmail
            db2 = local_mongo['mm-mc'].invalidqq

############################################################
# 信号量处理
def signal_handle(mode):
    log.info("catch signal: %s" % mode)
    global signal_stop
    signal_stop = True

# ----------------------------------
def main():
    init()
    init_gevent_signal(signal_handle)
    gevent.joinall([
        gevent.spawn(init_router),

        gevent.spawn(fetchmongo),
        gevent.spawn(fetchmongo),
        gevent.spawn(fetchmongo),

        gevent.spawn(localsave),
        gevent.spawn(localsave),
        gevent.spawn(localsave),
        gevent.spawn(localsave),
        gevent.spawn(localsave),

        gevent.spawn(localsave),
        gevent.spawn(localsave),
        gevent.spawn(localsave),
        gevent.spawn(localsave),
        gevent.spawn(localsave),

        gevent.spawn(localsave),
        gevent.spawn(localsave),
        gevent.spawn(localsave),
        gevent.spawn(localsave),
        gevent.spawn(localsave),
    ])

if __name__ == "__main__":
    log.info("program start...")
    main()
    log.info("program quit...")