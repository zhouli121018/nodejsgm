#!/usr/local/pyenv/versions/edm_web/bin/python
# -*- coding: utf-8 -*-
#
"""
每隔一小时执行
1. 腾讯企业邮箱：获取发送失败和不存在的地址。
2. 真实成功率统计
3. 统计客户10个任务的平均发送成功率
"""
from gevent import monkey
monkey.patch_all()
import gevent
import gevent.pool

import os
import re
import sys
import time
import datetime
import redis
import traceback
import logging
import logging.handlers

from collections import defaultdict
from email.parser import Parser
from newlib import common, filetools, pidfile, db_utils, parse_email, html2text, search_mail_status
from imapclient import IMAPClient

# 全局变量
log = None
signal_stop = False
glb_count_task = None
glb_count_send = None
glb_p_date=None
glb_p_hour=None
glb_time_b=None
glb_time_e=None
glb_process_log_list=None

SCRIPT = os.path.realpath(os.path.join(os.path.split(__file__)[0]))
GLB_PG_LOG_DBNAME = 'pgsql_log'
GLB_MY_MS_DBNAME = 'mysql_ms'
COMMON_VAR_COUNT_HASH = 'common_var_count_hash'

# 收件人域名设置
GLB_QQ_DOMAIN = 'qq.com'
GLB_163_DOMAIN = ['163.com', '126.com']
# 待统计的域名列表
GLB_DOMAINS = ['qq.com', '163.com', '*']

GLB_RE_PATTERN_1 = re.compile(ur'无法发送到\s+((\w|[-+=.])+@\w+([-.]\w+)*\.(\w+))')
GLB_RE_PATTERN_2 = re.compile(ur'不存在')
GLB_RE_PATTERN_3 = re.compile(ur'邮箱空间不足')
GLB_RE_PATTERN_4 = re.compile(ur'said:\s+(.*?\))')

GLB_IMAP_HOSTNAME = 'imap.exmail.qq.com' #gmail的smtp服务器网址

redis_pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
redis = redis.StrictRedis(connection_pool=redis_pool)

_loop_dict = lambda : defaultdict(_loop_dict)

############################################################
# 日志设置
def set_logger(log_file, is_screen=True):
    global log
    log = logging.getLogger('stat_log')
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

############################################################
# 开始结束处理
# 初始化
def init():
    global glb_p_date, glb_p_hour, glb_time_b, glb_time_e, glb_process_log_list, glb_count_task, glb_count_send
    task_count = 10
    send_count = 100
    sql = "SELECT task_count, send_count, domain FROM stat_task_setting LIMIT 1;"
    res = common.time_call(db_utils.query, GLB_MY_MS_DBNAME, sql)
    if res:
        task_count = res[0][0]
        send_count = res[0][1]
        stat_domain_T = res[0][2]

    # 统计任务个数
    glb_count_task = task_count
    # 统计发送数量大于等于
    glb_count_send = send_count

    t = time.localtime(time.time() - 60 * 60 * 1)
    glb_p_date = time.strftime("%Y-%m-%d", t)
    glb_p_hour = int(time.strftime("%H", t))

    # 根据指定的小时生成要处理的时间区间
    glb_time_b = "%02d:00:00" % glb_p_hour
    glb_time_e = "%02d:00:00" % (glb_p_hour + 1)
    log.info('StatLog, date: %s, hour: %s, time range: %s - %s' % (glb_p_date, glb_p_hour, glb_time_b, glb_time_e))

    glb_process_log_list = []
    datfile = os.path.join(SCRIPT, 'data', 'logstat.dat')
    if os.path.exists(datfile):
        for line in file(datfile).read().strip().split("\n"):
            glb_process_log_list.append(line)

# 结束
# 添加已处理记录
def finishProcess():
    datfile = os.path.join(SCRIPT, 'data', 'logstat.dat')

    # 添加日期、时间片数值加至处理队列
    glb_process_log_list.insert(0, glb_p_date + ',' + str(glb_p_hour))

    # 判断是否
    c_pop = len(glb_process_log_list) - 80
    if c_pop > 0:
        for i in range(0, c_pop):
            glb_process_log_list.pop()

    # 保存数据至文件
    try:
        logdata = "\n".join(glb_process_log_list)
        file(datfile, 'w').write(logdata)
    except Exception, e:
        log.error(traceback.format_exc())

    return

# 异常处理
def exitProcess():
    # 判断是否和当前时间段相同，如相同则忽略
    if glb_p_date == time.strftime("%Y-%m-%d") and glb_p_hour == int(time.strftime("%H")):
        log.info('StatLog ignore ({},{}), it current time'.format(glb_p_date, glb_p_hour))
        return 2

    # 检测当前时间段是否已处理过
    if '{},{}'.format(glb_p_date, glb_p_hour) in glb_process_log_list:
        log.info('StatLog ignore ({},{}), it has been processed'.format(glb_p_date, glb_p_hour))
        return 2

    if not checkTableExist:
        log.info('StatLog not found data table, ignored')
        return 2

    return 1

# 检测 日志表格是否存在
def checkTableExist():
    tb_name = "maillog_%s" % (glb_p_date.replace('-', ''))
    sql = "SELECT tablename FROM pg_tables WHERE tablename='%s';" % tb_name
    res = db_utils.query(GLB_PG_LOG_DBNAME, sql)
    if not res:
        return False
    return True


############################################################
# 有些测试用户故意测试加一些不存在的地址来测试，这些地址走SMTP账号通道发送后，没有错误回执，
# 可以对中继平台的SMTP账号发出的邮件的日志做一个回传处理，，客户界面和管理员界面都能查询到发送失败和不存在的地址。
def getSmtpData():
    tb_name = "maillog_%s" % (glb_p_date.replace('-', ''))
    if glb_time_e == '24:00:00':
        sql = """
            SELECT log_id, smtp_account_id, mail_from, mail_to
            FROM %s
            WHERE send_time>='%s'
              AND is_ok='t' AND return_code='250'
              AND customer_id<>'0' AND smtp_account_id is not null;
        """ % (tb_name, glb_time_b)
    else:
        sql = """
            SELECT log_id, smtp_account_id, mail_from, mail_to
            FROM %s
            WHERE send_time>='%s' AND send_time<'%s'
              AND is_ok='t' AND return_code='250'
              AND customer_id<>'0' AND smtp_account_id is not null;
        """ % (tb_name, glb_time_b, glb_time_e)
    res = common.time_call(db_utils.query, GLB_PG_LOG_DBNAME, sql)
    smtp_dict = {}
    for log_id, smtp_account_id, mail_from, mail_to in res:
        log_id = int(log_id)
        smtp_account_id = int(smtp_account_id)
        if smtp_account_id not in smtp_dict:
            smtp_dict[smtp_account_id] = []

        smtp_dict[smtp_account_id].append(
            (log_id, mail_from, mail_to)
        )
    return smtp_dict

def do_email_text(text, mail_to):
    if mail_to not in text:
        return None, None

    m = GLB_RE_PATTERN_1.search(text)
    if m:
        email = m.group(1)
        if email != mail_to:
            return None, None

        m2 = GLB_RE_PATTERN_2.search(text)
        if m2:
            error_type = 1
            return_said = 'said: 550 [%s]: Recipient address rejected: Access denied' % mail_to
        else:
            m3 = GLB_RE_PATTERN_3.search(text)
            if m3:
                error_type = 2
                return_said = 'said: 552 Quota exceeded or service disabled.'
            else:
                error_type = 3
                return_said = 'said: 550 Message was blocked by server'
        m4 = GLB_RE_PATTERN_4.search(text)
        if m4:
            return_said = m4.group()
        return error_type, return_said
    return None, None

def do_email(msg_content, mail_to):
    # 稍后解析出邮件:
    msg = Parser().parsestr(msg_content)
    email_str = msg.as_string()
    p = parse_email.ParseEmail(email_str)
    m = p.parseMailTemplate()
    try:
        text = html2text.beautifulsoup_html2text(
            m.get('html_text', '').decode(
                m.get('html_charset', 'utf-8'), errors='ignore'
            ).encode('utf-8')
        )
        return do_email_text(text, mail_to)
    except:
        return None, None

def do_worker_imap_update(log_id, mail_to, return_said, error_type, mode='qq'):
    return_code = 450 if error_type==1 else 550
    tb_name = "maillog_%s" % (glb_p_date.replace('-', ''))
    sql = u"UPDATE {} SET return_code=%s, return_said=%s, error_type=%s, is_ok='f' WHERE log_id=%s;".format(tb_name)
    args = (return_code, return_said, error_type, log_id)
    res = common.time_call(db_utils.do, GLB_PG_LOG_DBNAME, sql, args)
    log.info(u'woker_imap {} log_id={}, mail_to={}, error_type={}, return_code={}, return_said={}'.format(mode, log_id, mail_to, error_type, return_code, return_said))
    # less stat_log.log | grep 'woker_imap log_id'
    return

def do_worker_qq(smtp_account, smtp_password, smtp_list):
    # 通过一下方式连接smtp服务器，没有考虑异常情况，详细请参考官方文档
    server = IMAPClient(GLB_IMAP_HOSTNAME, ssl= True)
    try:
        server.login(smtp_account, smtp_password)
        server.select_folder('INBOX')

        year, mouth, day = glb_p_date.split('-')
        date = datetime.date(int(year), int(mouth), int(day))
        date2 = date - datetime.timedelta(days=1)
        result = server.search(['UNSEEN', 'SINCE', date2])
        msgdict = server.fetch(result, ['BODY.PEEK[]'] )
        msgtuple=sorted(msgdict.items(), key=lambda e:e[0], reverse=True)

        log_ids = []
        for message_id, message in msgtuple:
            msg_content = message['BODY[]']
            for log_id, mail_from, mail_to in smtp_list:
                if log_id in log_ids: continue
                error_type, return_said = do_email(msg_content, mail_to)
                if error_type is not None:
                    log_ids.append(log_id)
                    do_worker_imap_update(log_id, mail_to, return_said, error_type)
                    server.add_flags(message_id, '\\seen')
    finally:
        server.logout()
    return

# ------------------------------------
def do_email_mailrelay(mail_to, mail_from, response_code, response_text):
    if response_code==200:
        for res in response_text['return_list']:
            if ( res['state'] == 'fail_finished' or res['state'] == 'reject' ) and res['mail_from'] == mail_from and res['mail_to'] == mail_to:
                if res['error_type'] == 2:
                    error_type = 1
                elif res['error_type'] == 4:
                    error_type = 2
                else:
                    error_type = 3
                deliver_ip = res['deliver_ip'] if res['deliver_ip'] else ''
                return_said = u'[{}]:{} {}'.format(deliver_ip, res['deliver_time'], res['return_message'])
                return error_type, return_said
    return None, None

def connect_mailrelay(url):
    retry = 10
    while retry:
        try:
            response_code, response_text = search_mail_status.Client(url).get_asset()
            return response_code, response_text
        except BaseException as e:
            log.error('connect_mailrelay url={}, retry={}'.format(url, retry))
            log.error(traceback.format_exc())
            retry -= 1
            gevent.sleep(3)
    return None

def do_worker_mailrelay(smtp_list):
    if smtp_list:
        mail_to_list = ','.join([res[2] for res in smtp_list])
        url = 'http://admin.mailrelay.cn/api_search/mail_status/?mail_to_list={}&search_date={}&search_hour={}&state={}'.format(
            mail_to_list, glb_p_date, glb_p_hour, 'fail_finished,reject'
        )
        res = connect_mailrelay(url)
        if res is None:
            log.error(u'do_worker_mailrelay smtp_list={}'.format(smtp_list))
            return
        response_code, response_text = res
        for log_id, mail_from, mail_to in smtp_list:
            error_type, return_said = do_email_mailrelay(mail_to, mail_from, response_code, response_text)
            if error_type is not None:
                do_worker_imap_update(log_id, mail_to, return_said, error_type, mode='mailrelay')
    return

def do_woker_imap(smtp_account_id, smtp_list):
    sql = """
      SELECT aa.account, aa.password, bb.smtp_server
        FROM core_mss_account aa
      INNER JOIN core_mss_server bb ON bb.type_id=aa.type_id
      WHERE aa.id=%d AND bb.smtp_server IN ('smtp.exmail.qq.com', 'smtp.mailrelay.cn')
      LIMIT 1;
      """ % (smtp_account_id, )
    res = common.time_call(db_utils.query, GLB_MY_MS_DBNAME, sql)
    if not res:  return
    smtp_account, smtp_password, smtp_server = res[0]
    if smtp_server == 'smtp.mailrelay.cn':
        do_worker_mailrelay(smtp_list)
    elif smtp_server == 'smtp.exmail.qq.com':
        do_worker_qq(smtp_account, smtp_password, smtp_list)
    return

def woker_imap():
    smtp_dict = getSmtpData()
    pool = gevent.pool.Pool(10)
    for smtp_account_id in smtp_dict:
        smtp_list = smtp_dict[smtp_account_id]
        pool.spawn(do_woker_imap, smtp_account_id, smtp_list)
    pool.join()
    return


############################################################
# 处理函数
# 统计指定日期的投递失败数据
def statErrorCountByDate():
    # 从数据库取得统计数据
    tb_name = "maillog_%s" % (glb_p_date.replace('-', ''))
    if glb_time_e == '24:00:00':
        sql = """
            WITH stat_domain_tmp AS(
                SELECT customer_id, task_ident, recv_domain, error_type, is_ok, COUNT(*) as stat_count
                    FROM %s
                WHERE send_time>='%s' AND customer_id<>'0' AND COALESCE(recv_domain, '') != ''
                GROUP BY customer_id, task_ident, recv_domain, error_type, is_ok
            ),
            stat_domain AS (
                SELECT customer_id, task_ident, error_type, is_ok, stat_count,
                    CASE WHEN recv_domain ='%s' THEN 'qq.com'
                        WHEN recv_domain IN %s THEN '163.com'
                        ELSE '*'
                    END AS recv_domain
                FROM stat_domain_tmp
            )
            SELECT customer_id, task_ident, error_type, is_ok, SUM(stat_count) AS stat_count, recv_domain
                FROM stat_domain
            GROUP BY customer_id, task_ident, error_type, is_ok, recv_domain
            ORDER BY customer_id, task_ident
        """ % (tb_name, glb_time_b,  GLB_QQ_DOMAIN, str(tuple(GLB_163_DOMAIN)))
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
                    CASE WHEN recv_domain ='%s' THEN 'qq.com'
                        WHEN recv_domain IN %s THEN '163.com'
                        ELSE '*'
                    END AS recv_domain
                FROM stat_domain_tmp
            )
            SELECT customer_id, task_ident, error_type, is_ok, SUM(stat_count) AS stat_count, recv_domain
                FROM stat_domain
            GROUP BY customer_id, task_ident, error_type, is_ok, recv_domain
            ORDER BY customer_id, task_ident
        """ % (tb_name, glb_time_b, glb_time_e, GLB_QQ_DOMAIN, str(tuple(GLB_163_DOMAIN)))
    res = common.time_call(db_utils.query, GLB_PG_LOG_DBNAME, sql)

    # 组合数据
    # stat_data = {}
    user_list = []
    stat_data = _loop_dict()
    for row in res:
        customer_id = int(row[0])
        # 初始化各域名统计数据
        t_ident = row[1]
        if not t_ident: continue
        recv_domain= row[5]
        # 统计计数
        count_err_1, count_err_2, count_err_3, count_err_5, count_success = 0, 0, 0, 0, 0
        if row[2] == 1:
            count_err_1 = row[4]
        if row[2] == 2:
            count_err_2 = row[4]
        if row[2] in [0, 3, 4, 6]:
            count_err_3 = row[4]
        if row[2] == 5:
            count_err_5 = row[4]
        if row[3]:
            count_success = row[4]
        _D = stat_data[customer_id][t_ident][recv_domain]
        _D['count_err_1'] = _D.get('count_err_1', 0) + count_err_1
        _D['count_err_2'] = _D.get('count_err_2', 0) + count_err_2
        _D['count_err_3'] = _D.get('count_err_3', 0) + count_err_3
        _D['count_err_5'] = _D.get('count_err_5', 0) + count_err_5
        _D['count_success'] = _D.get('count_success', 0) + count_success

        # 取得客户列表
        if customer_id not in user_list:
            user_list.append(customer_id)
    return stat_data, user_list


############################################################
# 真实发送数据统计
# 为 MySQL 数据库添加投递失败统计数据
def do_worker_stat(user_id, task_ident, recv_domain, detail_data):
    count_success = detail_data['count_success']
    count_error = detail_data['count_err_1'] + detail_data['count_err_2'] + detail_data['count_err_3'] + detail_data['count_err_5']
    log.info(u'worker_stat user_id={}, task_ident={}, domain={}, sned={}, success={}, err_5={}'.format(
        user_id, task_ident, recv_domain, count_success + count_error, count_success, detail_data['count_err_5']
    ))
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
    common.time_call(db_utils.do, GLB_MY_MS_DBNAME, sql)
    return

def worker_stat(stat_data):
    pool = gevent.pool.Pool(20)
    for user_id in stat_data:
        for task_ident in stat_data[user_id]:
            for recv_domain in stat_data[user_id][task_ident]:
                pool.spawn(do_worker_stat, user_id, task_ident, recv_domain, stat_data[user_id][task_ident][recv_domain])
            gevent.sleep(0.01)
    pool.join()
    return


############################################################
# 统计客户10个任务的平均发送成功率

def do_worker_task_update(user_id, domain, count_succ, count_succ_rej, count_sned, now):
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
    common.time_call(db_utils.do, GLB_MY_MS_DBNAME, sql)
    log.info(u'worker_task user_id={}, domain={}, avg_score={}, avg_score_s={}'.format(user_id, domain, avg_score, avg_score_s))
    return

def do_worker_task(user_id):
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
    res = common.time_call(db_utils.query, GLB_MY_MS_DBNAME, sql)

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
    for domain, score_T in domin_score.iteritems():
        count_succ_sum = float(sum( [i[0] for i in score_T] ))
        count_succ_rej_sum = float(sum( [i[1] for i in score_T] ))
        count_send_sum = float(sum( [i[2] for i in score_T] ))

        count_succ_all += count_succ_sum
        count_succ_rej_all += count_succ_rej_sum
        count_send_all += count_send_sum
        if domain == '*': continue
        do_worker_task_update(user_id, domain, count_succ_sum, count_succ_rej_sum, count_send_sum, now)
    if domin_score:
        domain = '*'
        do_worker_task_update(user_id, domain, count_succ_all, count_succ_rej_all, count_send_all, now)
    return

def worker_task(user_list):
    pool = gevent.pool.Pool(5)
    for user_id in user_list:
        pool.spawn(do_worker_task, user_id)
        gevent.sleep(0.01)
    pool.join()
    return


############################################################
# redis服务 统计各个区间分数的客户数
def do_redis_count_s(start, end, domain):
    sql = "SELECT COUNT(*) FROM core_customer_score WHERE score_s>=%d AND score_s<%d AND domain='%s';" % ( start, end, domain )
    res = common.time_call(db_utils.query, GLB_MY_MS_DBNAME, sql)
    return res[0][0]

def do_redis_count(start, end, domain):
    sql = "SELECT COUNT(*) FROM core_customer_score WHERE score>=%d AND score<%d AND domain='%s';" % ( start, end, domain )
    res = common.time_call(db_utils.query, GLB_MY_MS_DBNAME, sql)
    return res[0][0]

def do_worker_redis_count(domain, start, end):
    score_key = 'score_{}_{}'.format(domain.replace('.', '_'), start)
    score_s_key = 'score_s_{}_{}'.format(domain.replace('.', '_'), start)

    count = do_redis_count(start, end, domain)
    redis.hset( 'edm_web_core_customer_score', key=score_key, value='{}'.format(count) )

    count_s = do_redis_count_s(start, end, domain)
    redis.hset( 'edm_web_core_customer_score', key=score_s_key, value='{}'.format(count_s) )

    log.info('worker_redis range: {}-{}, domain: {}, count: {}, count_s: {}'.format( start, end, domain, count, count_s))
    return

def do_worker_redis_special(domain, start, end):
    for start_T in range(start, end, 2):
        end_T = start_T + 2
        do_worker_redis_count(domain, start_T, end_T)
    return

def do_worker_redis(domain, start, end):
    if start == 90:
        do_worker_redis_special(domain, start, end)
        return
    do_worker_redis_count(domain, start, end)
    return

def worker_redis():
    pool = gevent.pool.Pool(10)
    for start in range(0, 100, 10):
        for domain in GLB_DOMAINS:
            end = start + 10
            pool.spawn(do_worker_redis, domain, start, end)
    pool.join()
    return

############################################################
# 主函数
def main():
    init()

    status = exitProcess()
    if status == 2: return

    log.info('start woker_imap.....')
    woker_imap()
    log.info('finish woker_imap.....')
    gevent.sleep(0.01)

    stat_data, user_list = statErrorCountByDate()
    log.info('start worker_stat.....')
    worker_stat(stat_data)
    log.info('finish worker_stat.....')
    gevent.sleep(0.01)

    log.info('start worker_task.....')
    worker_task(user_list)
    log.info('finish worker_task.....')
    gevent.sleep(0.01)

    log.info('start worker_redis.....')
    worker_redis()
    log.info('finish worker_redis.....')

    finishProcess()
    return

if __name__ == "__main__":
    log_dir = os.path.join(SCRIPT, 'log')
    pid_dir = os.path.join(SCRIPT, 'pid')
    data_dir = os.path.join(SCRIPT, 'data')
    filetools.make_dir([log_dir, pid_dir, data_dir])
    log_file = os.path.join(log_dir, 'stat_log.log')
    set_logger(log_file)

    pid_file = os.path.join(pid_dir, 'stat_log.pid')
    pidfile.register_pidfile(pid_file)

    log.info(u'program start...')
    t1 = time.time()
    EXIT_CODE = 0
    try:
        main()
    except KeyboardInterrupt:
        signal_handle('sigint')
    except:
        log.error(traceback.format_exc())
        EXIT_CODE = 1
    log.info(u"program spend total time: {}".format(time.time()-t1))
    log.info(u"program quit...")
    sys.exit(EXIT_CODE)
