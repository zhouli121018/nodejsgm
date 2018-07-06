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

_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)s %(message)s'))
log = logging.getLogger('stat_log_test')
log.addHandler(_handler)
log.setLevel(logging.DEBUG)

############################################################
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
    # glb_p_date = time.strftime("%Y-%m-%d", t)
    # glb_p_hour = int(time.strftime("%H", t))

    glb_p_date = '2017-08-14'
    glb_p_hour = 11

    # 根据指定的小时生成要处理的时间区间
    glb_time_b = "%02d:00:00" % glb_p_hour
    glb_time_e = "%02d:00:00" % (glb_p_hour + 1)

    log.info('StatLog, date: %s, hour: %s, time range: %s - %s' % (glb_p_date, glb_p_hour, glb_time_b, glb_time_e))

    # glb_process_log_list = []
    # datfile = os.path.join(SCRIPT, 'data', 'logstat.dat')
    # if os.path.exists(datfile):
    #     for line in file(datfile).read().strip().split("\n"):
    #         glb_process_log_list.append(line)

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
            if res['state'] == 'fail_finished' and res['mail_from'] == mail_from and res['mail_to'] == mail_to:
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
            mail_to_list, glb_p_date, glb_p_hour, 'fail_finished'
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
# 主函数
def main():
    init()

    log.info('start woker_imap.....')
    woker_imap()
    log.info('finish woker_imap.....')
    gevent.sleep(0.01)
    return

if __name__ == "__main__":


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
