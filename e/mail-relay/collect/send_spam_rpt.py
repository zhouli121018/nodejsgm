# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
该脚本有两次运用
１．每天凌晨定时执行一次　　默认的　#python send_spam_rpt.py
２．每分钟执行一次　检测是否有自定义发送时间的　#python send_spam_rpt.py customer_sendtime
"""

from gevent import monkey

monkey.patch_time()
monkey.patch_socket()

import re
import os
import sys
import time
import smtplib
import logging
import random
import gevent
import gevent.pool
import traceback
import lib.common

lib.common.init_django_enev()

from apps.core.models import ColCustomerDomain, Customer, CustomerSetting
from apps.collect_mail.models import get_mail_model
from apps.mail.models import SpamRptSettings, SpamRptBlacklist
from deliver.lib.utility import RetryQueue, address_domain, decode_msg
from django.db import InterfaceError, DatabaseError, connection
from datetime import timedelta, datetime
from email.mime.text import MIMEText
from email.header import Header
from django import template
from django.template import Context, loader

_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)s %(message)s'))

log = logging.getLogger('spam_rpt')
log.addHandler(_handler)
log.setLevel(logging.DEBUG)

# 变量
_DEBUG = False
signal_stop = False
_MAXTHREAD = 50
html_template = ""
sender_from = 'spamreport@spamgateway.cn'

field_values = {
    '{id}': u'{{d.id}}',  # 邮件ID
    '{customer}': u'{{d.customer|default_if_none:""}}',  # 客户
    '{mail_id}': u'{{d.mail_id|default_if_none:"0"}}',  # 关联同一封邮件的Mail ID
    '{check_result}': u'{{d.get_check_result_display|default_if_none:""}}',  #检测结果（在垃圾邮件中表示隔离原因）
    '{check_message}': u'{{d.check_message|default_if_none:""}}',  #详细检测结果
    '{created}': u'{{d.created|date:"Y-m-d H:i:s"}}',  #隔离时间
    '{review_result}': u'{{d.get_review_result_display|default_if_none:""}}',  #审核结果
    '{deliver_time}': u'{{d.deliver_time|date:"Y-m-d H:i:s"}}',  #发送时间
    '{deliver_ip}': u'{{d.deliver_ip|default_if_none:""}}',  #发送IP
    '{return_code}': u'{{d.return_code|default_if_none:"0"}}',  #返回值
    '{return_message}': u'{{d.return_message|default_if_none:""}}',  #返回结果
    '{mail_from}': u'{{d.mail_from|default_if_none:""}}',  #发件人
    '{sender_name}': u'{{d.sender_name|default_if_none:""}}',  #发件人姓名
    '{mail_to}': u'{{d.mail_to|default_if_none:""}}',  #收件人
    '{subject}': u'{{d.subject|default_if_none:""}}',  #主题
    '{client_ip}': u'{{d.client_ip|default_if_none:""}}',  #客户端IP
    '{state}': u'{{d.get_state_display|default_if_none:""}}',  #状态
    '{dspam_sig}': u'{{d.dspam_sig|default_if_none:""}}',  #dspam的signature
    '{size}': u'{{d.size|default_if_none:"0"}}',  #邮件大小
    '{error_type}': u'{{d.get_error_type_display|default_if_none:""}}',  #发送错误类型
    '{dspam_study}': u'{{d.get_dspam_study_display|default_if_none:""}}',  #dspam学习结果
    '{customer_report}': u'{{d.get_customer_report_display|default_if_none:""}}',  #客户垃圾举报
    '{server_id}': u'{{d.get_server_id_display|default_if_none:""}}',  #所在服务器的ID
    '{reviewer}': u'{{d.reviewer|default_if_none:""}}',  #审核人
    '{review_time}': u'{{d.created|date:"Y-m-d H:i:s"}}',  #审核时间
    '{attach_name}': u'{{d.attach_name|default_if_none:""}}',  #附件名称

    '<<collect_mail_targs>>': u'{% load collect_mail_tags %}',
    '<<virus_mail_count_targs>>': u'{{ virus_mails|length }}',
    '<<virus_mail_tags>>': u'{% for d in virus_mails %}',
    '<<endfor_targs>>': u'{% endfor %}',
    '<<other_mail_count_targs>>': u'{{ other_mails|length }}',
    '<<other_mail_targs>>': u'{% for d in other_mails %}',

    '<<virus_operate_targs>>': u'''<font size="-2">
    [ <a href="http://{{ d.server_id|get_spam_rpt_server }}/collect_mail_review/mail_modify_spam?auth_key={{ d.date_id|get_delete_auth_key }}&amp;id={{ d.date_id }}&amp;action=delete">
    <font color="red">删除</font></a> ]</font>''',

    '<<other_operate_targs>>': u'''<font size="-2">
    [ <a href="http://{{ d.server_id|get_spam_rpt_server }}/collect_mail_review/mail_modify_spam?auth_key={{ d.date_id|get_deliver_auth_key }}&amp;id={{ d.date_id }}&amp;action=deliver"><font color="blue">放
行</font></a> |
    <a href="http://{{ d.server_id|get_spam_rpt_server }}/collect_mail_review/mail_modify_spam?auth_key={{ d.date_id|get_whitelist_auth_key }}&amp;id={{ d.date_id }}&amp;action=whitelist"><font color="#2a702
a">白名单</font></a> |
    <a href="http://{{ d.server_id|get_spam_rpt_server }}/collect_mail_review/mail_modify_spam?auth_key={{ d.date_id|get_delete_auth_key }}&amp;id={{ d.date_id }}&amp;action=delete"><font color="red">删除</f
ont></a> ]
    </font>''',
}


def get_mail_date():
    mail_date = (datetime.today() + timedelta(-1)).strftime('%Y%m%d')
    return mail_date


def get_html_template():
    global html_template, m_html_template
    html_contents = SpamRptSettings.objects.all()
    html_template = html_contents[0].html_content
    html_template = html_template.replace('<!--', '').replace('-->', '')
    # html_template = re.sub(r'<!--', '', html_template)
    # html_template = re.sub(r'-->', '', html_template)
    for key in field_values:
        if key in html_template:
            html_template = re.sub(key, field_values[key], html_template)
    m_html_template = html_contents[0].m_html_content
    m_html_template = m_html_template.replace('<!--', '').replace('-->', '')
    for key in field_values:
        if key in m_html_template:
            m_html_template = re.sub(key, field_values[key], m_html_template)
            # app_root = lib.common.APP_ROOT
            # tmplatefile = os.path.join(app_root, 'template/send_spam_rpt_template.html')
            # with open(tmplatefile) as f:
            # html_template = f.read()


def get_mail_message(customer_id, mail_to, sender_from, type='customer', sendtime=None):
    mail_model = get_mail_model(get_mail_date())
    if type == 'customer':
        if sendtime:
            virus_mails = get_mails_from_sendtime(customer_id, sendtime, mail_to=mail_to, check_result='virus')
            other_mails = get_mails_from_sendtime(customer_id, sendtime, mail_to=mail_to, check_result='not_virus')
        else:
            virus_mails = mail_model.objects.filter(customer__id=customer_id, mail_to=mail_to, state='reject',
                                                    check_result='virus', review_result='reject')
            other_mails = mail_model.objects.filter(customer__id=customer_id, mail_to=mail_to, state='reject',
                                                    review_result='reject').exclude(check_result='virus')
        t = template.Template(html_template)
        mail_subject = u'[垃圾邮件隔离报告] {} — {}'.format(mail_to, datetime.today().strftime('%Y-%m-%d'))
    else:
        if sendtime:
            virus_mails = get_mails_from_sendtime(customer_id, sendtime, mail_to='', check_result='virus')
            other_mails = get_mails_from_sendtime(customer_id, sendtime, mail_to='', check_result='not_virus')
        else:
            virus_mails = mail_model.objects.filter(customer__id=customer_id, state='reject', check_result='virus',
                                                    review_result='reject').order_by('mail_to')
            other_mails = mail_model.objects.filter(customer__id=customer_id, state='reject',
                                                    review_result='reject').exclude(check_result='virus').order_by('mail_to')
        t = template.Template(m_html_template)
        mail_subject = u'[垃圾邮件隔离报告] {}'.format(datetime.today().strftime('%Y-%m-%d'))

    context = {
        'virus_mails': virus_mails,
        'other_mails': other_mails,
    }

    html_content = t.render(Context(context))

    mail_message = MIMEText(html_content, _subtype='html', _charset='utf-8')
    mail_message['Subject'] = Header(mail_subject, 'utf-8')
    mail_message['From'] = Header(sender_from, 'utf-8')
    mail_message['To'] = Header(mail_to, 'utf-8')
    return mail_message


def get_mail(customer_id, mail_to, type='customer', sendtime=None):
    if type == 'manager':
        try:
            mail_to = Customer.objects.get(id=customer_id).email
        except:
            mail_to = ''
    if SpamRptBlacklist.objects.filter(recipient=mail_to.lower(), disabled=False, customer_id=customer_id):
        log.info('SpamRptBlacklist:{}'.format(mail_to))
        return False
    if not mail_to:
        return False
    domain = address_domain(mail_to)
    mail_info = {
        'mail_from': sender_from,
        'mail_to': mail_to,
    }
    colCustomerDomain_obj_list = list(
        ColCustomerDomain.objects.filter(customer__id=customer_id, domain=domain, disabled=False)
        .exclude(customer__gateway_status='disabled'))
    if colCustomerDomain_obj_list:
        domain_obj = random.choice(colCustomerDomain_obj_list)
        mail_info.update({
            'addr_host': domain_obj.forward_address,
            'addr_port': domain_obj.port,
            'addr_is_ssl': domain_obj.is_ssl
        })
    else:
        mx_list = lib.common.query_mx(domain)
        try:
            mail_info['addr_host'] = mx_list[0][0]
        except:
            mail_info['addr_host'] = None
        mail_info['addr_port'] = 25
        mail_info['addr_is_ssl'] = False
        log.warning(u'spam_rpt send: address is None')

    mail_message = get_mail_message(customer_id, mail_to, sender_from, type=type, sendtime=sendtime)
    mail_info.update(mail_message=mail_message)
    return mail_info


def send(host, port, use_ssl, sender, receiver, message):
    deliver_ip = None
    receive_ip = None
    try:
        with gevent.Timeout(300):
            if use_ssl:
                s = smtplib.SMTP_SSL(host, port)
            else:
                s = smtplib.SMTP(host, port)
            deliver_ip = s.sock.getsockname()[0]
            receive_ip = s.sock.getpeername()[0]
            s.sendmail(sender, receiver, message)
            s.quit()
            code, msg = 250, 'ok'
    except smtplib.SMTPResponseException as e:
        code, msg = e.smtp_code, e.smtp_error
    except smtplib.SMTPRecipientsRefused as e:
        senderrs = e.recipients
        code, msg = senderrs[receiver]
    except gevent.Timeout:
        code, msg = -1, u'spam_rpt send timeout'
    except BaseException as e:
        log.error(u'spam_rpt send exception, host={}, sender={}, receiver={}'
                  .format(host, sender, receiver), exc_info=1)
        code, msg = -1, repr(e)
    return code, msg, deliver_ip, receive_ip


def work_send(customer_id, mail_to, type='customer', sendtime=None):
    """
    :param customer_id: 客户Id
    :param mail_to: 报告接收者
    :param type: customer or manager 区别：对“客户”或对"管理员"发送报告
    :param sendtime: 自定义报告时间，默认为None　表示凌晨执行
    :return:
    """
    time1 = time.time()
    mail_info = get_mail(customer_id, mail_to, type=type, sendtime=sendtime)
    if not mail_info:
        return
    code, msg, deliver_ip, receive_ip = send(
        mail_info['addr_host'], mail_info['addr_port'], mail_info['addr_is_ssl'],
        mail_info['mail_from'], mail_info['mail_to'], mail_info['mail_message'].as_string()
    )
    msg = decode_msg(msg)
    time2 = time.time()
    log.info(u'spam_rpt message info, mail_to={}, code={}, msg={}, address={}, time={}'
             .format(mail_info['mail_to'], code, msg, mail_info['addr_host'], time2 - time1))


def main():
    try:
        t3 = time.time()
        mail_model = get_mail_model(get_mail_date())
        mail_tuple_list = mail_model.objects.exclude(customer__gateway_status='disabled') \
            .filter(state='reject', mail_to__isnull=False, review_result='reject',
                    customer__customersetting__spamrpt=True, customer__customersetting__is_spamrpt_sendtime=False) \
            .distinct('customer_id', 'mail_to') \
            .values_list('customer_id', 'mail_to')

        pool = gevent.pool.Pool(_MAXTHREAD)
        for customer_id, mail_to in mail_tuple_list:
            pool.spawn(work_send, customer_id, mail_to, 'customer')

        log.info('waiting stop...')
        pool.join()
        t4 = time.time()
        log.info('spam_rpt send total time={}'.format(t4 - t3))
        return
    except (DatabaseError, InterfaceError) as e:
        log.error(u'DatabaseError', exc_info=1)
        connection.close()
    except BaseException as e:
        log.error(u'spam_rpt: exception', exc_info=1)
        gevent.sleep(10)


def manager_main():
    """
    跟客户管理员发送报告
    :return:
    """
    try:
        t3 = time.time()
        mail_model = get_mail_model(get_mail_date())
        customer_list = mail_model.objects.exclude(customer__gateway_status='disabled') \
            .filter(state='reject', mail_to__isnull=False, review_result='reject',
                    customer__customersetting__m_spamrpt=True, customer__customersetting__is_spamrpt_sendtime=False) \
            .distinct('customer_id') \
            .values_list('customer_id', flat=True)

        pool = gevent.pool.Pool(_MAXTHREAD)
        for customer_id in customer_list:
            pool.spawn(work_send, customer_id, '', 'manager')

        log.info('waiting stop...')
        pool.join()
        t4 = time.time()
        log.info('m_spam_rpt send total time={}'.format(t4 - t3))
        return
    except (DatabaseError, InterfaceError) as e:
        log.error(u'DatabaseError', exc_info=1)
        connection.close()
    except BaseException as e:
        log.error(u'spam_rpt: exception', exc_info=1)
        gevent.sleep(10)


def get_mails_from_sendtime(customer_id, sendtime, mail_to=None, check_result=None):
    """
    获取sendtime往前24个小时内的邮件数据
    :param customer_id:
    :param sendtime:
    :param mail_to:
    :param check_result:
    :return:
    """
    mail_model = get_mail_model(get_mail_date())
    mail_model_today = get_mail_model(time.strftime('%Y%m%d'))
    start_time = datetime.combine((datetime.today() + timedelta(-1)), sendtime)
    end_time = datetime.combine(datetime.today(), sendtime)
    first_mails = mail_model.objects.filter(customer_id=customer_id, state='reject', mail_to__isnull=False,
                                            review_result='reject', created__gte=start_time)
    last_mails = mail_model_today.objects.filter(customer_id=customer_id, state='reject', mail_to__isnull=False,
                                                 review_result='reject', created__lt=end_time)
    if check_result == 'virus':
        first_mails = first_mails.filter(check_result='virus')
        last_mails = last_mails.filter(check_result='virus')
    elif check_result == 'not_virus':
        first_mails = first_mails.exclude(check_result='virus')
        last_mails = last_mails.exclude(check_result='virus')

    if mail_to:
        first_mails = first_mails.filter(mail_to=mail_to)
        last_mails = last_mails.filter(mail_to=mail_to)
    else:
        first_mails = first_mails.order_by('mail_to')
        last_mails = last_mails.order_by('mail_to')
    mails = list(first_mails)
    mails.extend(list(last_mails))
    return mails


def customer_sendtime():
    """
    自定义时间发送报告
    :return:
    """
    try:
        t3 = time.time()
        pool = gevent.pool.Pool(_MAXTHREAD)
        for s in CustomerSetting.objects.filter(is_spamrpt_sendtime=True,
                                                spamrpt_sendtime__contains=time.strftime("%H:%M:")).exclude(
                customer__gateway_status='disabled'):
        # for s in CustomerSetting.objects.filter(is_spamrpt_sendtime=True).exclude(customer__gateway_status='disabled'):
            if s.spamrpt:
                mails = get_mails_from_sendtime(s.customer_id, s.spamrpt_sendtime)
                for mail_to in set([m.mail_to for m in mails]):
                    pool.spawn(work_send, s.customer_id, mail_to, 'customer', s.spamrpt_sendtime)
            if s.m_spamrpt:
                pool.spawn(work_send, s.customer_id, '', 'manager', s.spamrpt_sendtime)
        log.info('waiting stop...')
        pool.join()
        t4 = time.time()
        log.info('spam_rpt send total time={}'.format(t4 - t3))
        return
    except (DatabaseError, InterfaceError) as e:
        log.error(u'DatabaseError', exc_info=1)
        connection.close()
    except BaseException as e:
        log.error(u'spam_rpt: exception', exc_info=1)


# 信号量处理
def signal_handle(mode):
    log.info("catch signal: %s" % mode)
    global signal_stop
    signal_stop = True


if __name__ == '__main__':
    globals()['_DEBUG'] = lib.common.check_debug(2)
    lib.common.init_cfg_default()
    lib.common.init_run_user(lib.common.cfgDefault.get('global', 'user'))
    lib.common.init_makedir()
    lib.common.init_logger('SpamRpt', _DEBUG, _DEBUG)
    arg1 = sys.argv[1] if len(sys.argv) > 1 else ''

    get_html_template()
    EXIT_CODE = 0
    log.info("program start")
    try:
        lib.common.gevent_signal_init(signal_handle)
        # 自定义发送时间的
        if arg1 == 'customer_sendtime':
            customer_sendtime()
        else:
            # 默认凌晨发送的
            main()
            manager_main()
    except KeyboardInterrupt:
        signal_handle('sigint')
    except:
        log.error(traceback.format_exc())
        EXIT_CODE = 1
    log.info("program quit")
    sys.exit(EXIT_CODE)
