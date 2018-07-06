# -*- coding: utf-8 -*-
#
"""
DBL 黑名单移除
"""

from gevent import monkey
monkey.patch_all()
import gevent
import gevent.pool

import re
import time
import json
import requests
import random
import datetime
import traceback
from js2py import eval_js

from newlib.log import log
from newlib._signal import init_gevent_signal
from newlib import common, db_utils, sf_settings

MYSQL_MS = 'mysql_ms'
redis = db_utils.redis_db
signal_stop = False

############################################################
# 初始化
def init():
    expire_time = 5*24*60*60
    sql = "SELECT `customer_id`, `domain` FROM `core_domain` WHERE `status` IN ('Y', 'T');"
    res = common.time_call(db_utils.query, MYSQL_MS, sql)
    dbl_key = "domain:dbl:check"
    for customer_id, domain in res:
        if not domain: continue
        key = "domain:dbl:check:{}".format(domain)
        if not redis.exists(key):
            if not customer_id: customer_id=0
            p = redis.pipeline()
            p.lpush(dbl_key, json.dumps({ 'customer_id': customer_id, 'domain': domain }))
            p.set(key, 1)
            p.expire(key, expire_time)
            p.execute()

def init_routine():
    while True:
        if signal_stop: break
        try:
            log.info('init routine...')
            init()
            log.info('init routine finish...')
        except BaseException as e:
            log.error('init routine error...')
        gevent.sleep(7200)

############################################################
# 查询
def get_js_return(content):
    jschl_vc = None
    passwd = None
    jschl_answer = None

    l = re.findall(r'name="jschl_vc" value="(.*?)"', content)
    if l: jschl_vc = l[0]
    l = re.findall(r'name="pass" value="(.*?)"', content)
    if l: passwd = l[0]
    m = re.search(r'setTimeout\(function\(\)\{((?:.|\n)*?)f\.submit\(\)', content)
    if m:
        s = m.group(1)
        l = s.split("\n")
        l = [i for i in l if i.split()]
        first = l[0]
        last = l[-2]
        # log.info("----m: {}".format(m.group()))
        # log.info('------------------: {}'.format(first))
        # log.info('------------------: {}'.format(last))
        _ret = re.search(r"(.*?)a\.value\s+=\s+((.*?)121')", last)
        if _ret:
            last = _ret.group(1)
            ret = _ret.group(2)
        js = "function f(){ %s  %s  %s  return %s }" % (
            first,
            """
            t = 'https://www.spamhaus.org/';
            r = t.match(/https?:\/\//)[0];
            t = t.substr(r.length); t = t.substr(0,t.length-1);
          """,
            last,
            ret
        )
        jschl_answer = eval_js(js)()
    return jschl_vc, passwd, jschl_answer

def _search(d, dbl_err_key, j):
    customer_id, domain = j['customer_id'], j['domain']
    log.info("start customer_id: {}, domain: {}".format(customer_id, domain))
    url = "http://www.spamhaus.org/query/domain/{}".format(domain)
    https_url = "http://www.spamhaus.org/query/domain/{}".format(domain)
    ref_url = "http://www.spamhaus.org/query/domain/{}".format(domain)
    s = requests.session()
    proxies = next(sf_settings.CYCLE_PROXIES)
    log.info("domain: {}, proxies: {}".format(domain, proxies))
    s.proxies = proxies
    s.headers.update(sf_settings.HEADERS)
    s.headers.update({'User-Agent': random.choice(sf_settings.UA)})
    s.headers.update({'Referer': ref_url})

    r = s.get(https_url)
    jschl_vc, passwd, jschl_answer = get_js_return(r.content)
    log.info("jschl_vc: {}, passwd: {}, jschl_answer: {}".format(jschl_vc, passwd, jschl_answer))
    if jschl_answer is not None:
        payload = {'jschl_vc': jschl_vc, 'pass': passwd, 'jschl_answer': jschl_answer}
        time.sleep(4)
        s.get("https://www.spamhaus.org/cdn-cgi/l/chk_jschl?", params=payload)
        r = s.get(https_url)

    T = False
    content = r.content
    if content.find("is not listed in the DBL") > 0:
        T = True
        log.info("{} is not listed in the DBL".format(domain))
    if content.find("is listed in the DBL") > 0:
        T = True
        log.error("{} is listed in the DBL".format(domain))
        redis.lpush(dbl_err_key, d)
    if not T:
        raise Exception("query dbl with no response")
    return

def search():
    dbl_key = "domain:dbl:check"
    dbl_err_key = "domain:dbl:error"
    while True:
        if signal_stop: break
        _, d = redis.brpop(dbl_key)
        try:
            _search(d, dbl_err_key, json.loads(d) )
        except BaseException as e:
            redis.lpush(dbl_key, d)
            log.error(traceback.format_exc())
        gevent.sleep(10)

############################################################
def _save(j):
    customer_id, domain = j['customer_id'], j['domain']
    sql = "INSERT INTO `dbl_domain_log`(`customer_id`, `domain`, `status`, `created`) VALUES (%s, %s, %s, %s);"
    args = (customer_id, domain, 1, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    res = common.time_call(db_utils.do, MYSQL_MS, sql, args)

# 保存错误
def save():
    dbl_err_key = "domain:dbl:error"
    while True:
        if signal_stop: break
        _, d = redis.brpop(dbl_err_key)
        try:
            _save(json.loads(d) )
        except BaseException as e:
            redis.lpush(dbl_err_key, d)
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
        gevent.spawn(init_routine),
        gevent.spawn(search),
        gevent.spawn(save),
    ])

if __name__ == "__main__":
    log.info("program start...")
    main()
    log.info("program quit...")
