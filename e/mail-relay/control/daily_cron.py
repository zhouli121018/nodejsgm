# coding=utf-8
"""
每日定时任务：
１. 清空邮件备份日志
２. 检查用户是否过期
统计发送日志
"""
import os
import re
import sys
import traceback
import datetime
import shutil
import json

from lib.common import outerror, outinfo
import lib.common as Common
from lib.postfix_status import get_postfix_data


Common.init_django_enev()
from django.conf import settings
from django.db.models import Count, F

from apps.mail.models import Settings, get_mail_model, BulkCustomer, CheckStatistics, SubjectKeywordBlacklist, \
    KeywordBlacklist, ReviewStatistics, InvalidMail, TempSenderBlacklist, MailStateLog, DeliverLog, SenderCreditLog
from apps.core.models import Customer, PostfixStatus, CustomerSummary
from apps.collect_mail.models import CheckStatistics as ColCheckStatistics, get_mail_model as get_col_mail_model, \
    ReviewStatistics as ColReviewStatistics, MailStateLog as ColMailStateLog, DeliverLog as ColDeliverLog
from lib.statistic import save_statistic



class DefaultSetting(object):
    back_days = 30
    expired_days = 15
    invalid_mail_expire_days = 30


_DEBUG = False

setting = DefaultSetting()


def clear_email_back():
    """
    根据配置定时清除原始邮件
    :return:
    """
    outinfo('clear email back start')
    back_days = setting.back_days
    for d in range(back_days + 1, 90):
        path = os.path.join(settings.DATA_PATH, (datetime.date.today() - datetime.timedelta(days=d)).strftime('%Y%m%d'))
        if os.path.isdir(path):
            outinfo('remove path: {}'.format(path))
            shutil.rmtree(path)
    outinfo('clear email back end')

    for d in range(back_days + 1, 90):
        path = os.path.join(settings.DATA_PATH,
                            'c_{}'.format((datetime.date.today() - datetime.timedelta(days=d)).strftime('%Y%m%d')))
        if os.path.isdir(path):
            outinfo('remove path: {}'.format(path))
            shutil.rmtree(path)
    outinfo('clear collect email back end')

    outinfo('clear database start')
    MailStateLog.objects.filter(created__lt=(datetime.datetime.now() - datetime.timedelta(days=30))).delete()
    ColMailStateLog.objects.filter(created__lt=(datetime.datetime.now() - datetime.timedelta(days=30))).delete()
    DeliverLog.objects.filter(deliver_time__lt=(datetime.datetime.now() - datetime.timedelta(days=90))).delete()
    ColDeliverLog.objects.filter(deliver_time__lt=(datetime.datetime.now() - datetime.timedelta(days=90))).delete()
    SenderCreditLog.objects.filter(create_time__lt=(datetime.datetime.now() - datetime.timedelta(days=180))).delete()
    outinfo('clear database end')


def clear_invalid_email():
    """
    清除过期的无效地址
    :return:
    """
    outinfo('clear invalid start')
    expire_days = setting.invalid_mail_expire_days
    active_time = datetime.datetime.now() - datetime.timedelta(days=expire_days)
    InvalidMail.objects.filter(created__lte=active_time).delete()
    outinfo('clear invalid end')


def monitor_customer():
    """
    检测用户过期情况
    :return:
    """
    for c in Customer.objects.all():
        # 根据中继服务时间　判断中继客户状态
        service_end = c.service_end
        today = datetime.date.today()
        if service_end:
            if service_end <= today:
                if (service_end + datetime.timedelta(days=setting.expired_days) >= today) and c.company.find(
                        u'临时信任') == -1:
                    if c.status != 'expired':
                        c.status = 'expired'
                        c.save()
                        outinfo(u'用户过期: {}({})'.format(c.company, c.username))
                else:
                    if c.status != 'disabled':
                        c.status = 'disabled'
                        c.save()
                        outinfo(u'用户禁用: {}({})'.format(c.company, c.username))
            else:
                if service_end - datetime.timedelta(days=10) <= today:
                    if c.status != 'expiring':
                        c.status = 'expiring'
                        c.save()
                        outinfo(u'用户即将过期: {}({})'.format(c.company, c.username))
                else:
                    if c.status != 'normal':
                        c.status = 'normal'
                        c.save()
                        outinfo(u'启用用户: {}({})'.format(c.company, c.username))
        else:
            if c.status != 'disabled':
                c.status = 'disabled'
                c.save()
                outinfo(u'用户禁用(服务时间为空): {}({})'.format(c.company, c.username))

        #根据网关服务时间　判断网关客户状态
        service_end = c.gateway_service_end
        today = datetime.date.today()
        if service_end:
            if service_end <= today:
                if (service_end + datetime.timedelta(days=setting.expired_days) >= today) and c.company.find(
                        u'临时信任') == -1:
                    if c.gateway_status != 'expired':
                        c.gateway_status = 'expired'
                        c.save()
                        outinfo(u'用户过期: {}({})'.format(c.company, c.username))
                else:
                    if c.gateway_status != 'disabled':
                        c.gateway_status = 'disabled'
                        c.save()
                        outinfo(u'用户禁用: {}({})'.format(c.company, c.username))
            else:
                if service_end - datetime.timedelta(days=10) <= today:
                    if c.gateway_status != 'expiring':
                        c.gateway_status = 'expiring'
                        c.save()
                        outinfo(u'用户即将过期: {}({})'.format(c.company, c.username))
                else:
                    if c.gateway_status != 'normal':
                        c.gateway_status = 'normal'
                        c.save()
                        outinfo(u'启用用户: {}({})'.format(c.company, c.username))
        else:
            if c.gateway_status != 'disabled':
                c.gateway_status = 'disabled'
                c.save()
                outinfo(u'用户禁用(服务时间为空): {}({})'.format(c.company, c.username))

    """
    for c in ColCustomer.objects.all():
        service_end = c.service_end
        today = datetime.date.today()
        if service_end <= today:
            if service_end + datetime.timedelta(days=setting.expired_days) >= today:
                if c.status != 'expired':
                    c.status = 'expired'
                    c.save()
                    outinfo(u'collect用户过期: {}({})'.format(c.company, c.username))
            else:
                if c.status != 'disabled':
                    c.status = 'disabled'
                    c.save()
                    outinfo(u'collect用户禁用: {}({})'.format(c.company, c.username))
        else:
            if c.status != 'normal':
                c.status = 'normal'
                c.save()
                outinfo(u'collect启用用户: {}({})'.format(c.company, c.username))
    """


def _do_bulk_customer(date):
    print date
    bulk_max = setting.bulk_customer
    check_list = ['bulk_email', 'error_format', 'recipient_blacklist', 'spam']
    mail_model = get_mail_model(date.strftime('%Y%m%d'))
    customers = mail_model.objects.filter(check_result__in=check_list).values('customer').annotate(
        count=Count("customer")).filter(count__gt=bulk_max).order_by('-count')
    print customers
    for c in customers:
        customer = c['customer']
        sender_dict = mail_model.objects.filter(check_result__in=check_list, customer=customer).values(
            'mail_from').annotate(count=Count('mail_from')).order_by('-count')
        print sender_dict
        bulk_obj, _ = BulkCustomer.objects.get_or_create(customer_id=customer, date=date)
        bulk_obj.spam_count = c['count']
        bulk_obj.sender_count = len(sender_dict)
        bulk_obj.sender = json.dumps(list(sender_dict))
        bulk_obj.recent_count = BulkCustomer.objects.filter(customer=customer, date__lt=date,
                                                            date__gt=(date - datetime.timedelta(days=3))).count()
        bulk_obj.save()


def set_bulk_customer():
    outinfo('set bulk customer start')
    for d in range(1, -1, -1):
        date = datetime.date.today() - datetime.timedelta(days=d)
        _do_bulk_customer(date)
    outinfo('set bulk customer end')


def save_postfix_status():
    outinfo('save postfix start')
    for d in range(1, -1, -1):
        date = datetime.date.today() - datetime.timedelta(days=d)
        data = get_postfix_data(date)
        p, _ = PostfixStatus.objects.get_or_create(date=date, server_id=settings.SERVER_ID)
        p.connect_num = data.get('connect_num', 0)
        p.reject_num = data.get('reject_num', 0)
        p.pass_num = data.get('pass_num', 0)
        p.mail_num = p.reject_num + p.pass_num
        p.rate1 = data.get('rate1', 0)
        p.rate2 = data.get('rate2', 0)
        p.rate3 = data.get('rate3', 0)
        p.rate4 = data.get('rate4', 0)
        p.rate5 = data.get('rate5', 0)
        p.rate6 = data.get('rate6', 0)
        p.rate7 = data.get('rate7', 0)
        p.rate8 = data.get('rate8', 0)
        p.spf = data.get('spf', 0) + data.get('spf_error', 0)
        p.rbl = data.get('rbl', 0)
        p.save()
    outinfo('save postfix end')


def save_check_statistic(date, get_mail_model, statistics, check_list):
    model = get_mail_model(date.strftime('%Y%m%d'))
    all_dict = dict(model.objects.values_list("check_result").annotate(Count("id")))
    pass_dict = dict(
        model.objects.filter(review_result__in=['pass', 'pass_undo']).values_list("check_result").annotate(Count("id")))

    obj, _ = statistics.objects.get_or_create(date=date)
    for c in check_list:
        obj.__setattr__('{}_all'.format(c), all_dict.get(c, 0))
        obj.__setattr__('{}_pass'.format(c), pass_dict.get(c, 0))
    obj.save()


def check_statistic():
    outinfo('check statistic start')
    for d in range(2, 0, -1):
        date = datetime.date.today() - datetime.timedelta(days=d)
        check_list = ['active_spam', 'high_risk', 'keyword_blacklist', 'sender_blacklist', 'subject_blacklist',
                      'cyber_spam', 'spamassassin', 'high_sender']
        save_check_statistic(date, get_mail_model, CheckStatistics, check_list)
        check_list = ['high_risk', 'keyword_blacklist', 'sender_blacklist', 'subject_blacklist', 'cyber_spam',
                      'spamassassin']
        save_check_statistic(date, get_col_mail_model, ColCheckStatistics, check_list)
    outinfo('check statistic end')


def _do_save_keyword_review_status_auto_reject(date):
    """
    单独统计网关　免审关键字检测状态
    格式如下: 一级建造师----一级建造师(keyword_blacklist)
    :param date:
    :return:
    """
    res_dict = {}
    model = get_col_mail_model(date.strftime('%Y%m%d'))
    mails = model.objects.filter(check_result='auto_reject')
    for m in mails:
        check_message = m.check_message
        k = check_message.split('----')[0]
        check_result = re.findall('\((.*?)\)', check_message)
        if not check_result:
            continue
        check_result = check_result[0]
        res_dict.setdefault(check_result, {})
        if k in res_dict[check_result]:
            res_dict[check_result][k] += 1
        else:
            res_dict[check_result][k] = 1
    print res_dict
    for k, v in res_dict.iteritems():
        if k == 'subject_blacklist':
            blacklist_model = SubjectKeywordBlacklist
        else:
            blacklist_model = KeywordBlacklist
        for k1, v1 in v.iteritems():
            objs = blacklist_model.objects.filter(keyword=k1)
            if objs:
                obj = objs[0]
                obj.collect_all += v1
                obj.save()


def _do_save_keyword_review_status(date, get_mail_model, check_result, relay=True):
    model = get_mail_model(date.strftime('%Y%m%d'))
    mails = model.objects.filter(check_result=check_result)
    subject_dict = {}
    subject_pass_dict = {}
    for m in mails:
        k = m.check_message.split('----')[0]
        if k in subject_dict:
            subject_dict[k] += 1
        else:
            subject_dict[k] = 1
        if m.state != 'reject':
            if k in subject_pass_dict:
                subject_pass_dict[k] += 1
            else:
                subject_pass_dict[k] = 1
    if check_result == 'subject_blacklist':
        blacklist_model = SubjectKeywordBlacklist
    else:
        blacklist_model = KeywordBlacklist

    for k, v in subject_dict.iteritems():
        objs = blacklist_model.objects.filter(keyword=k)
        if objs:
            obj = objs[0]
            if relay:
                obj.relay_all += v
            else:
                obj.collect_all += v
            if k in subject_pass_dict:
                if relay:
                    obj.relay_pass += subject_pass_dict[k]
                else:
                    obj.collect_pass += subject_pass_dict[k]
            obj.save()


def save_keyword_review_status():
    """
    统计某个关键字 检测次数和 通过次数
    :return:
    """
    outinfo('save keword review status start')
    for d in range(2, 0, -1):
        date = datetime.date.today() - datetime.timedelta(days=d)
        _do_save_keyword_review_status(date, get_mail_model, 'subject_blacklist', relay=True)
        _do_save_keyword_review_status(date, get_mail_model, 'keyword_blacklist', relay=True)
        _do_save_keyword_review_status(date, get_col_mail_model, 'subject_blacklist', relay=False)
        _do_save_keyword_review_status(date, get_col_mail_model, 'keyword_blacklist', relay=False)
        _do_save_keyword_review_status_auto_reject(date)
    outinfo('save keword review status end')


def save_review_statistic(date, get_mail_model, statistics, check_list, type='all'):
    model = get_mail_model(date.strftime('%Y%m%d'))
    mails = model.objects.filter(check_result__in=check_list)
    if type == 'all':
        _save_review_statistic(model, date, mails, statistics, type)
    else:
        reviewers = set(mails.filter(reviewer__isnull=False).values_list('reviewer', flat=True))
        for r in reviewers:
            _ = mails.filter(reviewer_id=r)
            _save_review_statistic(model, date, _, statistics, type, r)


def _save_review_statistic(model, date, mails, statistics, type='all', reviewer=None):
    review_all = mails.count()
    review_reject = mails.filter(state='reject').count()
    review_pass = review_all - review_reject
    if type == 'all':
        review_pass_undo = model.objects.filter(review_result='pass_undo').count()
        review_reject_undo = model.objects.filter(review_result='reject_undo').count()
    else:
        review_pass_undo = mails.filter(review_result='pass_undo').count()
        review_reject_undo = mails.filter(review_result='reject_undo').count()
    review_undo = review_reject_undo + review_pass_undo
    timedeltas = mails.filter(review_time__isnull=False). \
        annotate(time=F('review_time') - F('created')).values_list('time', flat=True)
    times = (sum(timedeltas, datetime.timedelta()) / len(timedeltas)).total_seconds() if timedeltas else 0
    if reviewer:
        print reviewer
        obj, _ = statistics.objects.get_or_create(date=date, type=type, reviewer_id=reviewer)
    else:
        obj, _ = statistics.objects.get_or_create(date=date, type=type)
    obj.review_all = review_all
    obj.review_reject = review_reject
    obj.review_pass = review_pass
    obj.review_pass_undo = review_pass_undo
    obj.review_reject_undo = review_reject_undo
    obj.review_undo = review_undo
    obj.times = times
    obj.save()


def review_statistic():
    """
    邮件审核人员管理：
         1、统计审核的邮件总数，通过/拒绝的邮件数
         2、统计邮件平均审核时间，就是待审核邮件的平均等待时间。
         3、统计邮件的审核正确率，xx.xx%显示格式（被其他人员纠正的邮件，就是误判的邮件）
    :return:
    """
    outinfo('review statistic start')
    for d in range(2, 0, -1):
        date = datetime.date.today() - datetime.timedelta(days=d)
        print date
        check_list = ['active_spam', 'high_risk', 'keyword_blacklist', 'sender_blacklist', 'subject_blacklist',
                      'cyber_spam', 'spamassassin', 'recipient_blacklist']
        save_review_statistic(date, get_mail_model, ReviewStatistics, check_list, 'all')
        save_review_statistic(date, get_mail_model, ReviewStatistics, check_list, 'reviewer')
        check_list = ['high_risk', 'keyword_blacklist', 'sender_blacklist', 'subject_blacklist',
                      'cyber_spam', 'spamassassin', 'spf', 'force_check']
        save_review_statistic(date, get_col_mail_model, ColReviewStatistics, check_list, 'all')
        save_review_statistic(date, get_col_mail_model, ColReviewStatistics, check_list, 'reviewer')
    outinfo('review statistic end')


def clear_temp_sender_black_list():
    """
    清除过期的发件人黑名单
    :return:
    """
    TempSenderBlacklist.objects.filter(expire_time__lt=datetime.datetime.now()).delete()


def _summary(date, ctype='relay'):
    mail_model = get_mail_model if ctype == 'relay' else get_col_mail_model
    mail_model = mail_model(date.strftime('%Y%m%d'))
    for c in mail_model.objects.values('customer').annotate(count=Count("customer")).order_by('-count'):
        try:
            customer = Customer.objects.get(pk=c['customer'])
        except:
            continue
        count_limit = customer.relay_limit if ctype == 'relay' else customer.collect_limit
        if ctype == 'relay':
            count = mail_model.objects.exclude(mail_from='<>', mail_from__isnull=False).filter(
                customer=customer).distinct('mail_from').count()
        else:
            count = mail_model.objects.exclude(mail_to='<>', mail_to__isnull=False).filter(
                customer=customer, state='finished').distinct('mail_to').count()
        exceed = True if count_limit != -1 and count > count_limit else False
        obj, _ = CustomerSummary.objects.get_or_create(customer=customer, date=date)
        if ctype == 'relay':
            obj.relay_count = count
            obj.relay_limit = count_limit
            obj.is_relay_limit = exceed
        else:
            obj.collect_count = count
            obj.collect_limit = count_limit
            obj.is_collect_limit = exceed
        if exceed:
            if ctype == 'relay':
                customer.relay_exceed += 1
            else:
                customer.collect_exceed += 1
            customer.save()
        obj.save()
        save_statistic(obj, ctype)


def customer_summary():
    """
    统计客户每天的发送状态
    :return:
    """
    for d in range(2, -1, -1):
        date = datetime.date.today() - datetime.timedelta(days=d)
        _summary(date, 'relay')
        _summary(date, 'collect')


def gen_spamassassin_cf():
    """
    根据主题/内容关键字信息每天生成Spamassassin配置文件供windows邮件系统用
    :return:
    """
    cf_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../web_customer/static/spamassassin/'))

    subject_template = u"""\r\nheader CN_SUBJECT_{index}	Subject =~ /{subject}/\r\ndescribe CN_SUBJECT_{index}	Subject contains "{subject}"\r\nscore CN_SUBJECT_{index}	10\r\n"""
    subject_origin_cf = os.path.join(cf_path, 'CN_Spam_Subject_origin.cf')
    subject_cf = os.path.join(cf_path, 'CN_Spam_Subject.cf')
    shutil.copyfile(subject_origin_cf, subject_cf)

    fw = open(subject_cf, 'a')
    index = 10001
    for s in SubjectKeywordBlacklist.objects.filter(c_direct_reject=True):
        try:
            fw.write(subject_template.format(**{'index': index, 'subject': s}).encode('gb2312'))
        except:
            pass
        index += 1
    fw.close()

    body_template = u"""\r\nbody CN_BODY_{index}	/{body}/\r\ndescribe CN_BODY_{index}	Body contains "{body}"\r\nscore CN_BODY_{index}	10\r\n"""
    body_origin_cf = os.path.join(cf_path, 'CN_Spam_Body_origin.cf')
    body_cf = os.path.join(cf_path, 'CN_Spam_Body.cf')
    shutil.copyfile(body_origin_cf, body_cf)

    fw = open(body_cf, 'a')
    index = 10001
    for s in KeywordBlacklist.objects.filter(c_direct_reject=True):
        try:
            fw.write(body_template.format(**{'index': index, 'body': s}).encode('gb2312'))
        except:
            pass
        index += 1
    fw.close()


def init_resource():
    global setting

    settings = Settings.objects.all()
    if settings:
        setting = settings[0]


if __name__ == "__main__":
    globals()['_DEBUG'] = Common.check_debug(2)
    Common.init_cfg_default()
    Common.init_run_user(Common.cfgDefault.get('daily_cron', 'user'))
    Common.init_pid_file('Daily_cron.pid')
    Common.init_logger('Daily_cron', len(sys.argv) > 1, _DEBUG)

    # 运行程序
    EXIT_CODE = 0
    outinfo("program start")
    init_resource()

    try:
        clear_email_back()
        monitor_customer()
        customer_summary()
        set_bulk_customer()
        save_postfix_status()
        check_statistic()
        save_keyword_review_status()
        review_statistic()
        clear_invalid_email()
        clear_temp_sender_black_list()
        gen_spamassassin_cf()
    except:
        outerror(traceback.format_exc())
        EXIT_CODE = 1
    outinfo("program quit")
    sys.exit(EXIT_CODE)

