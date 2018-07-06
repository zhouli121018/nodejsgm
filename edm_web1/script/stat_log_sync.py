# -*- coding: utf-8 -*-
#
"""
公共处理程序
"""
import subprocess
from gevent import monkey
monkey.patch_all()

import gevent
import gevent.pool

import os
import re
import sys
import time
import traceback

from collections import defaultdict

import django
ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../edm_web'))
SCRIPT = os.path.join(ROOT, 'script')
sys.path.append(ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edm_web.settings")
django.setup()

from django.db import InterfaceError, DatabaseError, connections
from django.db.models import Q

from django.conf import settings
from django_redis import get_redis_connection
from app.address.models import MailList, MailListLog
from app.core.models import Customer
from app.setting.models import NoticeSetting, NoticeSettingDetail
from app.core.configs import NOTIFICATION_TYPE

from lib import pidfile, tools

import logging
import logging.handlers

# 全局变量
signal_stop = False
_MAXTHREAD = 20

redis = get_redis_connection()

# 统计指定日期的投递失败数据
def statErrorCountByDate(tablename, time_s=None, time_e=None):
    # 从数据库取得统计数据
    cr = time_call(get_ms_cr, 'pgsql-log')
    if time_s:
        if time_e == '24:00:00':
            sql = """
            WITH stat_domain_tmp AS(
                SELECT customer_id, task_ident, recv_domain, error_type, is_ok, COUNT(*) as stat_count
                    FROM %s
                WHERE send_time>='%s' AND customer_id<>'0' AND COALESCE(recv_domain, '') != ''
                GROUP BY customer_id, task_ident, recv_domain, error_type, is_ok
            ),
            stat_domain AS (
                SELECT customer_id, task_ident, error_type, is_ok, stat_count,
                    CASE WHEN recv_domain ='qq.com' THEN 'qq.com'
                    WHEN recv_domain IN ('163.com','126.com') THEN '163.com'
                        ELSE '*'
                    END AS recv_domain
                FROM stat_domain_tmp
            )
            SELECT customer_id, task_ident, error_type, is_ok, SUM(stat_count) AS stat_count, recv_domain
                FROM stat_domain
            GROUP BY customer_id, task_ident, error_type, is_ok, recv_domain
            ORDER BY customer_id, task_ident
            """ % (tablename, time_s)
        else:
            sql = """
            WITH stat_domain_tmp AS(
                SELECT customer_id, task_ident, recv_domain, error_type, is_ok, COUNT(*) as stat_count
                    FROM %s
                WHERE send_time>='%s' AND send_time<'%s' AND customer_id<>'0' AND COALESCE(recv_domain, '') != ''
                GROUP BY customer_id, task_ident, recv_domain, error_type, is_ok
            ),
            stat_domain AS (
                SELECT customer_id, task_ident, error_type, is_ok, stat_count,
                    CASE WHEN recv_domain ='qq.com' THEN 'qq.com'
                    WHEN recv_domain IN ('163.com','126.com') THEN '163.com'
                        ELSE '*'
                    END AS recv_domain
                FROM stat_domain_tmp
            )
            SELECT customer_id, task_ident, error_type, is_ok, SUM(stat_count) AS stat_count, recv_domain
                FROM stat_domain
            GROUP BY customer_id, task_ident, error_type, is_ok, recv_domain
            ORDER BY customer_id, task_ident
            """ % (tablename, time_s, time_e)
    else:
        sql = """
            WITH stat_domain_tmp AS(
                SELECT customer_id, task_ident, recv_domain, error_type, is_ok, COUNT(*) as stat_count
                    FROM %s
                WHERE customer_id<>'0' AND COALESCE(recv_domain, '') != ''
                GROUP BY customer_id, task_ident, recv_domain, error_type, is_ok
            ),
            stat_domain AS (
                SELECT customer_id, task_ident, error_type, is_ok, stat_count,
                    CASE WHEN recv_domain IN ('163.com', 'qq.com', '126.com') THEN recv_domain
                        ELSE '*'
                    END AS recv_domain
                FROM stat_domain_tmp
            )
            SELECT customer_id, task_ident, error_type, is_ok, SUM(stat_count) AS stat_count, recv_domain
                FROM stat_domain
            GROUP BY customer_id, task_ident, error_type, is_ok, recv_domain
            ORDER BY customer_id, task_ident
        """ % (tablename,)

    cr.execute(sql)
    res = cr.fetchall()
    # 组合数据
    stat_data = {}
    user_list = []
    for row in res:
        customer_id = int(row[0])
        # 初始化各域名统计数据
        t_ident = row[1]
        if not t_ident: continue

        recv_domain= row[5]

        # 初始化客户统计数据存储池
        if customer_id not in stat_data:
            stat_data[customer_id] = {}
        if t_ident not in stat_data[customer_id]:
            stat_data[customer_id][t_ident] = {}
        if recv_domain not in stat_data[customer_id][t_ident]:
            stat_data[customer_id][t_ident][recv_domain] = {
                'count_err_1': 0,
                'count_err_2': 0,
                'count_err_3': 0,
                'count_err_5': 0,
                'count_success': 0,
            }

        count_err_1, count_err_2, count_err_3, count_err_5, count_success = 0, 0, 0, 0, 0
        # 统计计数
        if row[2] == 1:
            stat_data[customer_id][t_ident][recv_domain]['count_err_1'] += row[4]
        if row[2] == 2:
            stat_data[customer_id][t_ident][recv_domain]['count_err_2'] += row[4]
        if row[2] in [0, 3, 4, 6]:
            stat_data[customer_id][t_ident][recv_domain]['count_err_3'] += row[4]
        if row[2] == 5:
            stat_data[customer_id][t_ident][recv_domain]['count_err_5'] += row[4]
        if row[3]:
            stat_data[customer_id][t_ident][recv_domain]['count_success'] += row[4]

        # 取得客户列表
        if customer_id not in user_list:
            user_list.append(customer_id)
    return stat_data, user_list

############################################################
# 真实发送数据统计
# 为 MySQL 数据库添加投递失败统计数据
def do_worker_day(user_id, task_ident, recv_domain, detail_data):
    count_success = detail_data['count_success']
    count_error = detail_data['count_err_1'] + detail_data['count_err_2'] + detail_data['count_err_3'] + detail_data['count_err_5']
    log.info(u'worker_stat user_id={}, task_ident={}, domain={}, sned={}, success={}, err_5={}'.format(
        user_id, task_ident, recv_domain, count_success + count_error, count_success, detail_data['count_err_5']
    ))
    cr = time_call(get_ms_cr, 'mm-ms')
    t = time.localtime(time.time())
    now = time.strftime("%Y-%m-%d %H:%M:%S", t)
    sql = """
    INSERT INTO stat_task_real (customer_id, task_ident, domain, count_send, count_error, count_err_1, count_err_2, count_err_3, count_err_5, created, updated)
        VALUES (%d, '%s', '%s', %d, %d, %d, %d, %d, %d, '%s', '%s')
        ON DUPLICATE KEY UPDATE
                  count_send=count_send + VALUES(count_send),
                  count_error=count_error + VALUES(count_error),
                  count_err_1=count_err_1 + VALUES(count_err_1),
                  count_err_2=count_err_2 + VALUES(count_err_2),
                  count_err_3=count_err_3 + VALUES(count_err_3),
                  count_err_5=count_err_5 + VALUES(count_err_5),
                  updated=VALUES(updated);
    """ % (
        user_id, task_ident, recv_domain,
        count_success + count_error, count_error,
        detail_data['count_err_1'], detail_data['count_err_2'],
        detail_data['count_err_3'], detail_data['count_err_5'],
        now, now
    )
    cr.execute(sql)
    return

############################################################
def worker_day(tablename):
    stat_data, user_list = statErrorCountByDate(tablename, time_s=None, time_e=None)
    for user_id in stat_data:
        for task_ident in stat_data[user_id]:
            for recv_domain in stat_data[user_id][task_ident]:
                do_worker_day(user_id, task_ident, recv_domain, stat_data[user_id][task_ident][recv_domain])
    return

############################################################
# 其他
def worker_other():
    stat_data, user_list = statErrorCountByDate('maillog_20170808', time_s='00:00:00', time_e='14:00:00')
    pool1 = gevent.pool.Pool(20)
    for user_id in stat_data:
        for task_ident in stat_data[user_id]:
            for recv_domain in stat_data[user_id][task_ident]:
                pool1.spawn(do_worker_day, user_id, task_ident, recv_domain, stat_data[user_id][task_ident][recv_domain])
                gevent.sleep(0.01)
    pool1.join()
    return

############################################################
# 统计客户10个任务的平均发送成功率

def do_worker_task_update(cr, user_id, domain, count_succ, count_succ_rej, count_sned, now):
    avg_score = round( count_succ*100.00 / count_sned, 2) if count_sned else 0
    avg_score_s = round( count_succ_rej*100.00 / count_sned, 2) if count_sned else 0

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

def do_worker_task(user_id):
    cr = time_call(get_ms_cr, 'mm-ms')
    log.info(u'worker_task user_id={}'.format(user_id))
    t = time.localtime(time.time())
    now = time.strftime("%Y-%m-%d %H:%M:%S", t)
    sql = """
    SELECT count_send, count_error, count_err_5, domain
    FROM stat_task_real
    WHERE customer_id=%d AND count_send > %d
    ORDER BY task_ident DESC
    LIMIT %d
    """ % (user_id, 100, 10)
    cr.execute(sql)
    res = cr.fetchall()

    domin_score = defaultdict(list)
    for count_send, count_error, count_err_5, domain in res:
        # 成功
        count_succ = count_send - count_error
        # 除去拒发
        count_succ_rej = count_send - count_error + count_err_5
        domin_score[domain].append(
            (count_succ, count_succ_rej, count_send)
        )

    count_send_all = 0
    count_succ_all = 0
    count_succ_rej_all = 0
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

# 统计平均成功率
def worker_success():
    cr = time_call(get_ms_cr, 'mm-ms')
    sql = "SELECT DISTINCT customer_id FROM stat_task_real;"
    cr.execute(sql)
    res = cr.fetchall()
    user_list = map(int, [i[0] for i in res])

    pool2 = gevent.pool.Pool(10)
    for user_id in user_list:
        pool2.spawn(do_worker_task, user_id)
        gevent.sleep(0.01)
    pool2.join()
    return

############################################################
# redis服务 统计各个区间分数的客户数

def do_worker_redis(domain, index):
    start = (index-1) * 10
    end = index*10
    score_key = 'score_{}_{}'.format(domain.replace('.', '_'), index)
    score_s_key = 'score_s_{}_{}'.format(domain.replace('.', '_'), index)

    sql = "SELECT COUNT(*) FROM core_customer_score WHERE score>=%d AND score<%d AND domain='%s';" % ( start, end, domain)
    cr = time_call(get_ms_cr, 'mm-ms')
    cr.execute(sql)
    res = cr.fetchall()
    count = res[0][0]

    redis.hset(
        'edm_web_core_customer_score', key=score_key, value='{}'.format(count)
    )

    sql = "SELECT COUNT(*) FROM core_customer_score WHERE score_s>=%d AND score_s<%d AND domain='%s';" % ( start, end, domain)
    cr.execute(sql)
    res = cr.fetchall()
    count_s = res[0][0]
    redis.hset(
        'edm_web_core_customer_score', key=score_s_key, value='{}'.format(count_s)
    )

    log.info('worker_redis range: {}-{}, domain: {}, count: {}, count_s: {}'.format( start, end, domain, count, count_s))
    return

def worker_redis():
    T = ['163.com', 'qq.com', '*']
    pool = gevent.pool.Pool(10)
    for index in xrange(1,11):
        for domain in T:
            pool.spawn(do_worker_redis, domain, index)
    pool.join()
    return

############################################################
# 主程序
def main():
    init()

    # log.info('start worker_other.....')
    # worker_other()
    # log.info('finish worker_other.....')
    # gevent.sleep(0.1)

    log.info('start worker_day.....')
    pool = gevent.pool.Pool(10)
    for tablename in glb_maillog_tables:
        pool.spawn(worker_day, tablename)
        gevent.sleep(0.02)
    pool.join()
    gevent.sleep(0.1)
    log.info('finish worker_day.....')


    log.info('start worker_success.....')
    worker_success()
    log.info('finish worker_success.....')

    log.info('start worker_success.....')
    worker_success()
    log.info('finish worker_success.....')

    log.info('start worker_redis.....')
    worker_redis()
    log.info('finish worker_redis.....')

    return

############################################################
def init():
    global glb_maillog_tables
    cr = time_call(get_ms_cr, 'pgsql-log')
    sql = """SELECT  tablename  FROM  pg_tables
        WHERE tablename LIKE 'maillog_201701%' OR tablename LIKE 'maillog_201702%' OR tablename LIKE 'maillog_201703%'
        OR tablename LIKE 'maillog_201704%' OR tablename LIKE 'maillog_201705%'
        ;"""
    cr.execute(sql)
    res = cr.fetchall()
    glb_maillog_tables = [i[0] for i in res]
    return


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
    log = logging.getLogger('stat_log_sync')
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
    log_file = os.path.join(log_dir, 'stat_log_sync.log')
    set_logger(log_file)

    pid_file = os.path.join(pid_dir, 'stat_log_sync.pid')
    pidfile.register_pidfile(pid_file)

    log.info(u'Program start...')
    main()
    log.info(u"Program quit...")