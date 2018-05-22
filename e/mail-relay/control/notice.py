# -*-coding:utf8-*-
#
"""
消息通知发送
每分钟检测状态　并触发发送各类通知
如：群发通知，　审核通知
"""

import sys
import re

import datetime
import time
import traceback

import gevent
import gevent.pool
from gevent import monkey

import lib.common as Common

monkey.patch_all()
Common.init_django_enev()

from django.db.models import Count
from django.db import InterfaceError, DatabaseError, connection
from django.conf import settings
from lib.common import outinfo, outerror
from lib.email_sender import MailSender
from lib.sms_sender import JiuTian
from lib.django_redis import get_redis
from django.contrib.auth.models import User
from apps.core.models import CustomerSetting, ColCustomerDomain, Notification, Customer
from apps.mail.models import BounceSettings, NoticeSettings, get_mail_model
from apps.collect_mail.models import get_mail_model as get_mail_model2


# ###########################################################
# 变量
_DEBUG = False
# 数据库设置
bounce_setting = None
notice_setting = None


def notice(subject, content, type='', customer=None, manager=None):
    """
    发送各类通知
    :return:
    """
    # 用户是否开启了邮件/消息通知设置
    is_notice = True
    if customer:
        is_notice = CustomerSetting.objects.filter(customer=customer, notice=True).first()

    if customer and type in ['c_service', 'r_service']:
        is_notice = CustomerSetting.objects.filter(customer=customer, service_notice=True).first()

    # 邮件通知
    is_email = False
    receiver = None
    if customer and customer.email:
        receiver = customer.email
    elif manager and manager.email:
        receiver = manager.email
    if receiver and is_notice:
        s = MailSender()
        code, msg = s.send_email(bounce_setting.server, bounce_setting.port, bounce_setting.mailbox,
                                 bounce_setting.password,
                                 receiver, subject, content)
        if code == 250:
            is_email = True

    # 短信通知
    is_sms = False
    mobile = None
    if customer and customer.mobile:
        mobile = customer.mobile
    elif manager and manager.phone_number:
        mobile = manager.phone_number

    if type in ['collect', 'relay', 'c_service', 'r_service']:
        mobile = None

    if mobile and is_notice:
        s = JiuTian()
        s.set_account(userid=settings.JIUTIAN_ID, passwd=settings.JIUTIAN_PASSWD, channel=settings.JIUTIAN_CHANNEL)
        try:
            s.send_sms(mobile, content)
            is_sms = True
        except:
            outerror(traceback.format_exc())

    # 站内通知
    Notification.objects.create(subject=subject, content=content, type=type, customer=customer, manager=manager,
                                is_email=is_email, is_sms=is_sms, is_notice=True)
    outinfo(u'type:{}, customer:{}, manager:{}, email:{}, mobile:{}'.format(type, customer, manager, receiver, mobile))


def bulk_notice():
    """
    群发邮件通知　用户群发邮件的时候通知客户和对应的技术支持
    :return:
    """
    global notice_setting, bounce_setting
    subject = u'违规邮件通知'
    while True:
        try:
            mail_model = get_mail_model(time.strftime('%Y%m%d'))
            if notice_setting:
                outinfo('bulk notice')
                bulk_count = notice_setting.bulk_count
                bulk_interval = notice_setting.bulk_interval
                content_format = notice_setting.bulk_content
                customers = mail_model.objects.filter(state='reject').values('customer').annotate(
                    count=Count("customer")).filter(count__gt=bulk_count).order_by('-count')
                for c in customers:
                    customer = Customer.objects.get(pk=c['customer'])
                    need_time = datetime.datetime.now() - datetime.timedelta(minutes=bulk_interval)
                    # 判断是否在发送间隔时间内, 如果在间隔时间内，则不发送通知
                    if Notification.objects.filter(customer=customer, created__gt=need_time, type='bulk'):
                        gevent.sleep(300)
                        continue
                    """
                    # 当天群发超过300 发通知一次   发第二次时检测 是否超过300*2  第三次是否超过300*3 依次类推
                    # 当天已发送群发通知的数量
                    times = Notification.objects.filter(customer=customer, created__contains=datetime.date.today(),
                                                        type='bulk').count()
                    if not times:
                        times = 1
                    if bulk_count and count > bulk_count * times:
                    """
                    notices = Notification.objects.filter(customer=customer, created__contains=datetime.date.today(), type='bulk').order_by('-created')
                    if notices:
                        count = mail_model.objects.filter(state='reject', customer=customer, created__gt=notices[0].created).count()
                    else:
                        count = c['count']
                    if count > bulk_count:
                        mails = mail_model.objects.exclude(mail_from='<>').filter(state='reject', customer=customer)
                        if notices:
                            mails = mails.filter(created__gt=notices[0].created)
                        sender_dict = mails.values('mail_from').annotate(count=Count('mail_from')).filter(count__gt=10).order_by('-count')
                        if sender_dict:
                            account_list = []
                            for s in sender_dict:
                                mail_from = re.sub('prvs=(.*?)=', '', s['mail_from'])
                                if mail_from not in account_list:
                                    account_list.append(mail_from)
                                if len(account_list) >= 7:
                                    break
                            content = Common.safe_format(content_format, count=str(count),
                                                         account=','.join(account_list))
                            notice(subject, content, 'bulk', customer)
            gevent.sleep(300)
        except (DatabaseError, InterfaceError), e:
            # 如果报数据库异常，关闭连接，重新处理任务
            outerror('DatabaseError')
            outerror(traceback.format_exc())
            connection.close()
            gevent.sleep(2)
        except:
            outerror(traceback.format_exc())
        gevent.sleep(300)


def get_review_count(get_mail_model):
    date_end = datetime.datetime.today()
    date_start = date_end - datetime.timedelta(days=3)
    date = date_start
    count = 0
    while date <= date_end:
        count += get_mail_model(date.strftime('%Y%m%d')).objects.exclude(check_result='cyber_spam').filter(
            state='review').count()
        date = date + datetime.timedelta(days=1)
    return count


def get_mail_count(get_mail_model, state):
    date_end = datetime.datetime.today()
    date_start = date_end - datetime.timedelta(days=3)
    date = date_start
    count = 0
    while date <= date_end:
        count += get_mail_model(date.strftime('%Y%m%d')).objects.filter(state=state).count()
        date = date + datetime.timedelta(days=1)
    return count


def review_notice():
    """
    审核邮件通知　需审核的邮件超过XXX封（中继+网关-cyber）发送通知给默认审核人员
    :return:
    """
    global notice_setting, bounce_setting
    subject = u'审核邮件通知'
    type = 'review'
    while True:
        try:
            if notice_setting:
                outinfo('review notice')
                review_count = notice_setting.review_count
                review_interval = notice_setting.review_interval
                content_format = notice_setting.review_content
                reviewer = notice_setting.reviewer
                need_time = datetime.datetime.now() - datetime.timedelta(minutes=review_interval)

                # 判断是否在发送间隔时间内, 如果在间隔时间内，则不发送通知
                if Notification.objects.filter(manager=reviewer, created__gt=need_time, type=type):
                    gevent.sleep(300)
                    continue
                count = get_mail_count(get_mail_model, 'review')
                # count = get_review_count(get_mail_model) + get_review_count(get_mail_model2)
                if count >= review_count:
                    content = Common.safe_format(content_format, count=str(count))
                    notice(subject, content, type, manager=reviewer)
            gevent.sleep(300)
        except:
            outerror(traceback.format_exc())
        gevent.sleep(300)


def ip_notice():
    """
    IP不通邮件通知　当发送机连续10分钟接收邮件都失败时，则通知相应管理员该发送机IP不通
    :return:
    """
    global notice_setting, bounce_setting
    subject = u'发送机IP不通通知'
    type = 'ip'
    redis = get_redis()
    while True:
        try:
            if notice_setting:
                outinfo('ip notice')
                ip_interval = notice_setting.ip_interval
                content_format = notice_setting.ip_content
                manager = notice_setting.manager
                need_time = datetime.datetime.now() - datetime.timedelta(minutes=ip_interval)
                _, ip = redis.brpop('control_dispatch_exception')

                # 判断是否在发送间隔时间内, 如果在间隔时间内，则不发送通知
                if Notification.objects.filter(manager=manager, created__gt=need_time, type=type,
                                               content__icontains=ip):
                    gevent.sleep(300)
                    continue
                content = Common.safe_format(content_format, ip=ip)
                notice(subject, content, type, manager=manager)
            gevent.sleep(300)
        except:
            outerror(traceback.format_exc())
        gevent.sleep(300)


def jam_notice():
    """
    实时监控服务器处理状态，当中继检测数＋中继传输数+中继重试数＋网关检测数超过阀值时，发送通知
    :return:
    """
    global notice_setting, bounce_setting
    subject = u'服务器拥堵通知'
    redis = get_redis()
    while True:
        try:
            if notice_setting:
                outinfo('jam notice')
                jam_interval = notice_setting.jam_interval
                content_format = notice_setting.jam_content
                count_max = notice_setting.jam_count
                manager = notice_setting.manager
                need_time = datetime.datetime.now() - datetime.timedelta(minutes=jam_interval)

                # 判断是否在发送间隔时间内, 如果在间隔时间内，则不发送通知
                if Notification.objects.filter(manager=manager, created__gt=need_time, type='jam'):
                    gevent.sleep(300)
                    continue

                relay_check = get_mail_count(get_mail_model, 'check')
                relay_dispatch = get_mail_count(get_mail_model, 'dispatch')
                relay_retry = get_mail_count(get_mail_model, 'retry')
                collect_check = get_mail_count(get_mail_model2, 'check')
                collect_send = get_mail_count(get_mail_model2, 'send')
                relay_error = Common.get_file_count('/home/umail/data/mails-error/')
                collect_error = Common.get_file_count('/home/umail/data/collect-mails-error/')
                count = relay_check + relay_dispatch + collect_check + collect_send + relay_retry + relay_error + collect_error
                if count >= count_max:
                    content = Common.safe_format(content_format, **locals())
                    notice(subject, content, 'jam', manager=manager)
            gevent.sleep(300)
        except:
            outerror(traceback.format_exc())
        gevent.sleep(300)


def collect_limit_notice():
    """
    定时一次性发送前一天的统计数据,hour_to设置定时发送时间，
    网关用户超过限制通知, 当用户超过设置值时，发送通知
    :return:
    """
    global notice_setting, bounce_setting
    hour_to = 1
    notice_type = "collect"
    while True:
        try:
            cur = datetime.datetime.now()
            if cur.hour == hour_to and notice_setting:
                outinfo('collect limit notice')
                all_content = ""
                content_format = notice_setting.collect_content
                manager = notice_setting.manager
                flag = Notification.objects.filter(manager=manager, type=notice_type,
                                                   created__contains=datetime.date.today())
                pre = cur + datetime.timedelta(-1)
                if not flag:
                    mail_model = get_mail_model2(pre.strftime('%Y%m%d'))
                    customers = mail_model.objects.exclude(customer__company__icontains=u'临时信任').values(
                        'customer').annotate(count=Count("customer")).order_by(
                        '-count')
                    for c in customers:
                        customer = Customer.objects.get(pk=c['customer'])
                        company_id = customer.id
                        company = customer.company
                        collect_limit = customer.collect_limit
                        rcp_count = mail_model.objects.exclude(mail_to='<>', mail_to__isnull=False).filter(
                            customer=customer).distinct('mail_to').count()
                        if collect_limit != -1 and rcp_count > collect_limit:
                            content = Common.safe_format(content_format, company=company, company_id=company_id,
                                                         setting=collect_limit, count=rcp_count)
                            all_content += content
                    if all_content:
                        subject = pre.strftime('%Y-%m-%d ') + u"网关用户超过限制通知"
                        notice(subject=subject, content=all_content, type=notice_type, customer=None, manager=manager)
        except:
            outerror(traceback.format_exc())
        finally:
            gevent.sleep(900)


def relay_limit_notice():
    """
    定时一次性发送
    中继用户超过限制通知, 当用户超过设置值时，发送通知
    :return:
    """
    global notice_setting, bounce_setting
    notice_type = "relay"
    while True:
        try:
            cur = datetime.datetime.now()
            if cur.hour != 1 or cur.minute != 25:
                gevent.sleep(30)
                continue
            outinfo('relay limit notice')
            all_content = ""
            content_format = notice_setting.relay_content
            manager = notice_setting.manager
            flag = Notification.objects.filter(manager=manager, type=notice_type,
                                               created__contains=datetime.date.today())
            pre = cur + datetime.timedelta(-1)
            if not flag:
                mail_model = get_mail_model(pre.strftime('%Y%m%d'))
                customers = mail_model.objects.exclude(customer__company__icontains=u'临时信任').values(
                    'customer').annotate(count=Count("customer")).order_by(
                    '-count')
                for c in customers:
                    customer = Customer.objects.get(pk=c['customer'])
                    company_id = customer.id
                    company = customer.company
                    relay_limit = customer.relay_limit
                    sender_count = mail_model.objects.exclude(mail_from='<>', mail_from__isnull=False).filter(
                        customer=customer).distinct('mail_from').count()
                    if relay_limit != -1 and sender_count > relay_limit:
                        content = Common.safe_format(content_format, company=company, company_id=company_id,
                                                     setting=relay_limit, count=sender_count)
                        all_content += content
                if all_content:
                    subject = pre.strftime('%Y-%m-%d ') + u"中继用户超过限制通知"
                    notice(subject=subject, content=all_content, type=notice_type, customer=None, manager=manager)
        except:
            outerror(traceback.format_exc())
        finally:
            gevent.sleep(60)


def collect_dielver_exception_notice():
    """
    网关客户服务器DOWN机要短信/邮件提醒管理员和客户管理员
    IP不通邮件通知　当发送机连续10分钟接收邮件都失败时，则通知相应管理员该发送机IP不通
    :return:
    """
    global notice_setting
    subject = u'网关客户服务器DOWN机通知'
    type = 'c_down'
    redis = get_redis()
    while True:
        try:
            if notice_setting:
                outinfo('collect deliver exception notice')
                interval = notice_setting.c_deliver_exception_interval
                content_format = notice_setting.c_deliver_exception_content
                manager = notice_setting.manager
                need_time = datetime.datetime.now() - datetime.timedelta(minutes=interval)
                _, res = redis.brpop('collect_deliver_exception')
                customer_id, domain = res.split(',')
                customer = Customer.objects.get(id=customer_id)
                ip = ','.join(list(
                    ColCustomerDomain.objects.filter(customer=customer, domain=domain, disabled=False).values_list(
                        'forward_address', flat=True)))
                if customer.gateway_status == 'disabled' or not ip or get_mail_model2(
                        datetime.date.today().strftime('%Y%m%d')).objects.filter(
                        state__in=['retry', 'send'], customer=customer).count() < 10:
                    continue

                # 判断是否在发送间隔时间内, 如果在间隔时间内，则不发送通知
                if Notification.objects.filter(customer=customer, created__gt=need_time, type=type):
                    gevent.sleep(300)
                    continue
                content = Common.safe_format(content_format, **locals())
                notice(subject, content, type, customer=customer)
                notice(subject, content, type, manager=customer.tech)
            gevent.sleep(300)
        except:
            outerror(traceback.format_exc())
        gevent.sleep(300)


def service_notice(type='relay'):
    """
    定时一次性发送
    中继/网关服务快到期之前15/7/3天提醒技术支持和客服
    :return:
    """
    global notice_setting, bounce_setting
    notice_type = "r_service" if type == 'relay' else 'c_service'
    type_info = u'中继' if type == 'relay' else u'网关'
    deal_days = [3, 7, 15]
    subject = u'{}服务到期提醒'.format(type_info)
    customer_content = notice_setting.service_limit_content
    while True:
        service_info = {}
        try:
            now = datetime.datetime.now()
            if now.hour != 1 or now.minute != 25:
                gevent.sleep(30)
                continue
            outinfo('service notice {}'.format(type))
            for days in deal_days:
                if type == 'relay':
                    customers = Customer.objects.filter(service_end=(now + datetime.timedelta(days=days)))
                else:
                    customers = Customer.objects.filter(gateway_service_end=(now + datetime.timedelta(days=days)))

                for customer in customers:
                    is_webmail_msg = u'(售后)' if customer.is_webmail else ''
                    msg = u"<a target='_blank' href='http://admin.mailrelay.cn/core/customer_list?customer_id={}'>{}</a>{}</br>".format(
                        customer.id, customer, is_webmail_msg)
                    service_info.setdefault(customer.service_id, {}).setdefault(days, []).append(msg)
                    service_info.setdefault(customer.tech_id, {}).setdefault(days, []).append(msg)
                    expire_date = (now + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
                    notice(subject=subject, content=customer_content.format(**locals()), type=notice_type,
                           customer=customer, manager=None)
            for s, info in service_info.iteritems():
                msg = ''
                for days in deal_days:
                    if days in info:
                        msg += u'{}服务{}天后({})到期客户</br>'.format(type_info, days,
                                                               (now + datetime.timedelta(days=days)).strftime(
                                                                   "%Y-%m-%d"))
                        msg += ''.join(info[days])
                if s:
                    user = User.objects.get(id=s)
                    notice(subject=subject, content=msg, type=notice_type, customer=None, manager=user)
        except:
            outerror(traceback.format_exc())
        finally:
            gevent.sleep(60)


# ###########################################################
# 初始化全局变量
def init_resource():
    global notice_setting, bounce_setting
    settings = NoticeSettings.objects.all()
    if settings:
        notice_setting = settings[0]
    settings = BounceSettings.objects.all()
    if settings:
        bounce_setting = settings[0]


def init_resource_routine():
    while True:
        try:
            outinfo('init resouce routine')
            init_resource()
        except BaseException as e:
            outerror('init_resource_routine exception')
        gevent.sleep(600)


# ###########################################################
def main():
    init_resource()
    gevent.joinall([
        gevent.spawn(init_resource_routine),
        gevent.spawn(service_notice, 'relay'),
        gevent.spawn(service_notice, 'collect'),
        gevent.spawn(bulk_notice),
        gevent.spawn(review_notice),
        gevent.spawn(ip_notice),
        gevent.spawn(jam_notice),
        gevent.spawn(collect_limit_notice),
        gevent.spawn(relay_limit_notice),
        gevent.spawn(collect_dielver_exception_notice),
    ])


if __name__ == "__main__":
    globals()['_DEBUG'] = Common.check_debug()
    Common.init_cfg_default()
    Common.init_run_user(Common.cfgDefault.get('global', 'user'))
    Common.init_pid_file('Notice.pid')
    Common.init_logger('Notice', len(sys.argv) > 1, _DEBUG)

    # 运行程序
    EXIT_CODE = 0
    outinfo("program start")
    main()
    outinfo("program quit")
    sys.exit(EXIT_CODE)
