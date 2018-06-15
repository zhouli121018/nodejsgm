# -*- coding: utf-8 -*-
#
from gevent import monkey
monkey.patch_all()

import gevent
import gevent.pool
import json
import datetime
import traceback
from libs import DB
from libs.log import loger
from libs._signal import init_gevent_signal
from libs.tools import validateQQ, validateEmail
try:
    from gevent.coros import RLock, Semaphore, BoundedSemaphore
except:
    from gevent.lock import BoundedSemaphore

log = loger("Test")
redis = DB.redis_db
sem = BoundedSemaphore(1) #设定对共享资源的访问数量 # only allows 1 greenlets at one time, others must wait until one is released

# 全局变量
signal_stop = False
LOCAL_MYSQL = "local_mysql"
LOCAL_PGSQL = "local_pgsql"
REMOTE_MYSQL = "remote_mysql"
REDIS_KEY = "cce7e4f11fc518f7fff230079ab0edc9"
# 收集QQ地址
GLB_REDIS_REMOTE_GET_QQ = "edm_web_qq_check_queue"

def init():
    p = redis.pipeline()
    p.sadd("remote:cce7e4f11fc518f7fff230079ab0edc9:listid:set", 0)
    p.expire("remote:cce7e4f11fc518f7fff230079ab0edc9:listid:set", 15*60*60*24)
    p.execute()

    sql = "SELECT `list_id` FROM `ml_maillist` WHERE `customer_id`=3;"
    res = DB.query("remote_myms", sql)
    key = "remote:cce7e4f11fc518f7fff230079ab0edc9:listid"
    for d in res:
        try:
            list_id = int(d[0])
            redis.lpush(key, list_id)
        except:
            pass

############################################################
def _remotefetch(list_id):
    addr_key = "remote:cce7e4f11fc518f7fff230079ab0edc9:addrs"
    sql = "SELECT `address`, `fullname` FROM `ml_subscriber_3` WHERE `list_id`=%s;"
    args = (list_id, )
    res = DB.query(REMOTE_MYSQL, sql, args)
    for d in res:
        address, fullname = d
        address = address and address.strip() or ""
        if not validateEmail(address): continue
        if validateQQ(address):
            redis.lpush(GLB_REDIS_REMOTE_GET_QQ, address)
        redis.lpush(addr_key, json.dumps({
            "addr": address,
            "name": fullname or "",
        }))

def remotefetch():
    key = "remote:cce7e4f11fc518f7fff230079ab0edc9:listid"
    semkey = "remote:cce7e4f11fc518f7fff230079ab0edc9:listid:set"
    while True:
        if signal_stop: break
        _, list_id = redis.brpop(key)
        if redis.sismember(semkey, list_id):
            continue
        try:
            log.info("start list_id: {}".format(list_id))
            _remotefetch(list_id)
            redis.sadd(semkey, list_id)
            log.info("finish list_id: {}".format(list_id))
        except BaseException as e:
            redis.lpush(key, list_id)
            log.error(traceback.format_exc())

############################################################
def _localhandle(j):
    addr, name = j["addr"], j["name"]
    log.info(j)
    now = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    # sql = """
    # INSERT INTO core_address(email, fullname, updated) VALUES (%s, %s, %s)
    # ON conflict (email) do UPDATE SET fullname=excluded.fullname, updated=excluded.updated;
    # """
    # args = ( addr, name, now )
    # DB.do( LOCAL_PGSQL, sql, args )

    sql = "SELECT id FROM core_address WHERE email=%s;"
    res = DB.queryone( LOCAL_PGSQL, sql, (addr, ) )
    if res:
        sql = """INSERT INTO core_address_attribute_rel(email_id, attribute_id, list_id, customer_id) VALUES (%s, 775, 387930, 2369);"""
        DB.do( LOCAL_PGSQL, sql, (res[0], ) )

def localhandle():
    category = "address"
    category_id = 29
    tag_id = 899
    # 地址维护表
    ADRESS_TABLE = "core_address"
    # 标签维护表
    ATTR_TABL = "core_attribute"
    # 地址属性关联表
    attribute_id = 775  # 插入关联表的属性ID
    REFER_TABLE = "core_address_attribute_rel"
    addr_key = "remote:cce7e4f11fc518f7fff230079ab0edc9:addrs"
    while True:
        if signal_stop: break
        _, d = redis.brpop(addr_key)
        try:
            _localhandle( json.loads(d) )
        except BaseException as e:
            redis.lpush(addr_key, d)
            log.error(traceback.format_exc())

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
        gevent.spawn(remotefetch),
        gevent.spawn(remotefetch),
        gevent.spawn(remotefetch),
        gevent.spawn(remotefetch),
        gevent.spawn(remotefetch),
    ])

if __name__ == "__main__":
    log.info("program start...")
    main()
    log.info("program quit...")
