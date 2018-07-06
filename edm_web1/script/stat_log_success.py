# -*- coding: utf-8 -*-
#
from gevent import monkey
monkey.patch_all()

import gevent
import gevent.pool

import os
import sys
import json
import time
import traceback
import logging
import logging.handlers

import django
ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../edm_web'))
SCRIPT = os.path.join(ROOT, 'script')
sys.path.append(ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edm_web.settings")
django.setup()
from django.conf import settings
from django.db import InterfaceError, DatabaseError, connections
from django_redis import get_redis_connection

from collections import defaultdict

from lib import pidfile, tools


# 全局变量
signal_stop = False
_MAXTHREAD = 20
glb_count_task=None
glb_count_send=None
glb_user_list=None

redis = get_redis_connection()

GLB_DOMAINS = ['qq.com', '163.com', '*']

############################################
# 统计平均成功率
def do_worker_task_update(cr, user_id, domain, count_succ, count_succ_rej, count_sned, now):
    avg_score = round( count_succ*100.00 / count_sned, 2) if count_sned else 0
    avg_score_s = round( count_succ*100.00 / count_succ_rej, 2) if count_succ_rej else 0
    sql = """
        INSERT INTO core_customer_score (customer_id, domain, score, score_s, created, updated)
        VALUES (%d, '%s', %.2f,  %.2f, '%s', '%s')
        ON DUPLICATE KEY UPDATE
                score=VALUES(score),
                score_s=VALUES(score_s),
                updated=VALUES(updated);
        """ % (
        user_id, domain, avg_score, avg_score_s, now, now
    )
    cr.execute(sql)
    log.info(u'worker_task user_id={}, domain={}, avg_score={}, avg_score_s={}'.format(user_id, domain, avg_score, avg_score_s))
    return

def worker(cr, user_id):
    log.info(u'worker_task user_id={}'.format(user_id))
    t = time.localtime(time.time())
    now = time.strftime("%Y-%m-%d %H:%M:%S", t)
    sql = """
    SELECT count_send, count_error, count_err_5, domain
    FROM stat_task_real
    WHERE customer_id=%d AND count_send > %d
    ORDER BY updated DESC
    LIMIT %d
    """ % (user_id, glb_count_send, glb_count_task)
    cr.execute(sql)
    res = cr.fetchall()

    domin_score = defaultdict(list)
    for count_send, count_error, count_err_5, domain in res:
        # 成功
        count_succ = count_send - count_error
        # 除去拒发
        count_succ_rej = count_send - count_err_5
        domin_score[domain].append(
            (count_succ, count_succ_rej, count_send)
        )

    count_send_all = 0
    count_succ_all = 0
    count_succ_rej_all = 0
    # log.info('-------------------qqqqq:user_id:{}--------domin_score:{}'.format(user_id, dict(domin_score)))
    for domain, score_T in domin_score.iteritems():
        count_succ_sum = float(sum( [i[0] for i in score_T] ))
        count_succ_rej_sum = float(sum( [i[1] for i in score_T] ))
        count_send_sum = float(sum( [i[2] for i in score_T] ))

        count_succ_all += count_succ_sum
        count_succ_rej_all += count_succ_rej_sum
        count_send_all += count_send_sum
        if domain == '*': continue
        do_worker_task_update(cr, user_id, domain, count_succ_sum, count_succ_rej_sum, count_send_sum, now)
    if domin_score:
        domain = '*'
        do_worker_task_update(cr, user_id, domain, count_succ_all, count_succ_rej_all, count_send_all, now)
    return


############################################################
# redis服务 统计各个区间分数的客户数
def do_redis_count_s(cr, start, end, domain):
    sql = "SELECT COUNT(*) FROM core_customer_score WHERE score_s>=%d AND score_s<%d AND domain='%s';" % ( start, end, domain )
    cr.execute(sql)
    res = cr.fetchall()
    return res[0][0]

def do_redis_count(cr, start, end, domain):
    sql = "SELECT COUNT(*) FROM core_customer_score WHERE score>=%d AND score<%d AND domain='%s';" % ( start, end, domain )
    cr.execute(sql)
    res = cr.fetchall()
    return res[0][0]

def do_worker_redis_count(cr, domain, start, end):
    score_key = 'score_{}_{}'.format(domain.replace('.', '_'), start)
    score_s_key = 'score_s_{}_{}'.format(domain.replace('.', '_'), start)

    count = do_redis_count(cr, start, end, domain)
    redis.hset( 'edm_web_core_customer_score', key=score_key, value='{}'.format(count) )

    count_s = do_redis_count_s(cr, start, end, domain)
    redis.hset( 'edm_web_core_customer_score', key=score_s_key, value='{}'.format(count_s) )

    log.info('worker_redis range: {}-{}, domain: {}, count: {}, count_s: {}'.format( start, end, domain, count, count_s))
    return

def do_worker_redis_special(cr, domain, start, end):
    for start_T in range(start, end, 2):
        end_T = start_T + 2
        do_worker_redis_count(cr, domain, start_T, end_T)
    return

def do_worker_redis(cr, domain, start, end):
    if start == 90:
        do_worker_redis_special(cr, domain, start, end)
        return
    do_worker_redis_count(cr, domain, start, end)
    return

def worker_redis(cr):
    pool = gevent.pool.Pool(10)
    for start in range(0, 100, 10):
        for domain in GLB_DOMAINS:
            end = start + 10
            pool.spawn(do_worker_redis, cr, domain, start, end)
    pool.join()
    return

# 主程序
def main():
    cr = time_call(get_ms_cr, 'mm-ms')
    init()
    pool = gevent.pool.Pool(5)
    for user_id in glb_user_list:
        pool.spawn(worker, cr, user_id)
        gevent.sleep(0.02)
    pool.join()

    worker_redis(cr)

    return

############################################################
def init():
    global glb_count_task, glb_count_send, glb_user_list
    cr = time_call(get_ms_cr, 'mm-ms')

    count_task = 10
    count_send = 100
    sql = "SELECT task_count, send_count FROM stat_task_setting LIMIT 1;"
    cr.execute(sql)
    res = cr.fetchall()
    if res:
        count_task = res[0][0]
        count_send = res[0][1]
    # 统计任务个数
    glb_count_task = count_task
    # 统计发送数量大于等于
    glb_count_send = count_send

    sql = "SELECT DISTINCT customer_id FROM stat_task_real;"
    cr.execute(sql)
    res = cr.fetchall()
    glb_user_list = map(int, [i[0] for i in res])

############################################################
# 安全调用对象
def safe_call(fn, *args, **kwargs):
    try :
        return fn(*args, **kwargs)
    except Exception, e:
        log.error('call "%s" failure\n %s' % (fn.__name__, e.message))
        log.error(traceback.format_exc())
        return None

# 等待调用成功 (有超时时间)
def time_call(fn, *args, **kwargs):
    try_count = 3
    while try_count > 0 :
        res = safe_call(fn, *args, **kwargs)
        if res is not None:
            return res
        log.error('try call "%s" count: %d' % (fn.__name__, try_count))
        try_count -= 1
        gevent.sleep(3)
    return

# 等待调用成功 (无超时时间)
def wait_call(fn, *args, **kwargs):
    while True :
        res = safe_call(fn, *args, **kwargs)
        if res is not None:
            return res
        gevent.sleep(3)
    return

def get_ms_cr(db_type):
    cr = connections[db_type].cursor()
    db = cr.db
    if db.connection is None or not db.is_usable():
        db.close_if_unusable_or_obsolete()
        with db.wrap_database_errors:
            db.connect()
        cr = connections[db_type].cursor()
        log.info(u'reconnect {} Connection end'.format(db_type))
        gevent.sleep(5)
    return cr

############################################################
# 日志设置
def set_logger(log_file, is_screen=True):
    global log
    log = logging.getLogger('stat_log_success')
    log.setLevel(logging.INFO)
    format = logging.Formatter('%(asctime)-15s %(levelname)s %(message)s')

    log_handler = logging.handlers.RotatingFileHandler(log_file, 'a', 5000000, 4)
    log_handler.setFormatter(format)
    log.addHandler(log_handler)
    f = open(log_file, 'a')
    sys.stdout = f
    # sys.stderr = f

    if is_screen:
        log_handler = logging.StreamHandler()
        log_handler.setFormatter(format)
        log.addHandler(log_handler)

# 信号量处理
def signal_handle(mode):
    log.info(u"Catch signal: %s" % mode)
    global signal_stop
    signal_stop = True

if __name__ == '__main__':
    log_dir = os.path.join(SCRIPT, 'log')
    pid_dir = os.path.join(SCRIPT, 'pid')
    data_dir = os.path.join(SCRIPT, 'data')
    tools.make_dir([log_dir, pid_dir, data_dir])
    log_file = os.path.join(log_dir, 'stat_log_success.log')
    set_logger(log_file)

    pid_file = os.path.join(pid_dir, 'stat_log_success.pid')
    pidfile.register_pidfile(pid_file)

    log.info(u'Program start...')
    main()
    log.info(u"Program quit...")
