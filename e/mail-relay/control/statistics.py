# coding=utf-8
"""
统计发送日志
"""
import sys
import traceback
import datetime
import re
import json

import lib.common as Common
from lib.common import outinfo, outerror


Common.init_django_enev()
from django.db.models import Count

from apps.mail.models import get_mail_model, Statistics, Settings, BulkCustomer
from apps.core.models import Cluster, IpPool
# from redis_cache import get_redis_connection
from lib.django_redis import get_redis
from apps.collect_mail.models import get_mail_model as get_collect_mail_model, Statistics as CStatistics


class DefaultSetting(object):
    back_days = 30


_DEBUG = False
redis = get_redis()
setting = DefaultSetting()


def get_data(mails):
    if not mails.count():
        return {}
    rs = {
        'count': mails.count(),
        'success': mails.filter(return_code=250).count()
    }
    rs['fail'] = rs['count'] - rs['success']
    error_list = mails.values_list('error_type').annotate(Count("id"))
    for l in error_list:
        error_type, count = l
        rs['error_type_{}'.format(error_type)] = count
    count = rs['count'] - rs.get('error_type_2', 0) - rs.get('error_type_4', 0) - rs.get('error_type_6', 0) - rs.get('error_type_7', 0)
    rs['rate'] = (float(rs['success']) / float(count)) * 100 if count else 0
    return rs


def save_statistics(obj, rs, collect=False):
    obj.count = rs.get('count', 0)
    obj.success = rs.get('success', 0)
    obj.fail = rs.get('fail', 0)
    obj.rate = rs.get('rate', 0)
    obj.error_type_1 = rs.get('error_type_1', 0)
    obj.error_type_2 = rs.get('error_type_2', 0)
    obj.error_type_3 = rs.get('error_type_3', 0)
    obj.error_type_4 = rs.get('error_type_4', 0)
    obj.error_type_5 = rs.get('error_type_5', 0)
    obj.error_type_6 = rs.get('error_type_6', 0)
    obj.error_type_7 = rs.get('error_type_7', 0)
    obj.error_type_8 = rs.get('error_type_8', 0)
    if collect:
        obj.mail_count = rs.get('mail_count', 0)
        obj.spam_count = rs.get('spam_count', 0)
        obj.spam_rate = rs.get('spam_rate', 0)
    obj.save()


def statistics(p_date):
    mails = get_mail_model(p_date.replace('-', '')).objects.filter(return_code__isnull=False)

    # type==all
    rs = get_data(mails)
    obj, bool = Statistics.objects.get_or_create(date=p_date, type='all')
    outinfo('all: {}'.format(rs))
    save_statistics(obj, rs)

    # type==ip
    ips = mails.values_list('deliver_ip', flat=True).distinct()
    for ip in ips:
        rs = get_data(mails.filter(deliver_ip=ip))
        if rs.get('count', 0):
            try:
                obj, bool = Statistics.objects.get_or_create(date=p_date, type='ip', ip=ip)
                save_statistics(obj, rs)
                outinfo('ip({}): {}'.format(ip, rs))
            except:
                outerror(traceback.format_exc())


    #type==ip_pool
    pools = IpPool.objects.all()
    for p in pools:
        ips = list(p.clusterip_set.values_list('ip', flat=True))
        rs = get_data(mails.filter(deliver_ip__in=ips))
        if rs.get('count', 0):
            try:
                obj, bool = Statistics.objects.get_or_create(date=p_date, type='ip_pool', ip_pool=p)
                save_statistics(obj, rs)
                outinfo('ip_pool({}): {}'.format(p, rs))
            except:
                outerror(traceback.format_exc())

    #type==cluster
    cls = Cluster.objects.all()
    for c in cls:
        ips = list(c.cluster.values_list('ip', flat=True))
        rs = get_data(mails.filter(deliver_ip__in=ips))
        if rs.get('count', 0):
            try:
                obj, bool = Statistics.objects.get_or_create(date=p_date, type='cluster', cluster=c)
                save_statistics(obj, rs)
                outinfo('cluster({}): {}'.format(c, rs))
            except:
                outerror(traceback.format_exc())

    #type==customer
    # customers = Customer.objects.all()
    customers = mails.values_list('customer_id', flat=True).distinct()
    for c in customers:
        rs = get_data(mails.filter(customer_id=c))
        if rs.get('count', 0):
            try:
                obj, bool = Statistics.objects.get_or_create(date=p_date, type='customer', customer_id=c)
                save_statistics(obj, rs)
                outinfo('customer({}): {}'.format(c, rs))
            except:
                outerror(traceback.format_exc())



def collect_statistics(p_date):
    all_mails = get_collect_mail_model(p_date.replace('-', '')).objects.all()
    mails = all_mails.filter(return_code__isnull=False)
    # mails = get_collect_mail_model(p_date.replace('-', '')).objects.filter(return_code__isnull=False)
    spam_mails = all_mails.filter(state='reject')

    # type==all
    rs = get_data(mails)
    mail_count = all_mails.count()
    spam_count = spam_mails.count()
    spam_rate = (float(spam_count) / float(mail_count)) * 100 if mail_count else 0
    rs.update(mail_count=mail_count, spam_count=spam_count, spam_rate=spam_rate)
    obj, bool = CStatistics.objects.get_or_create(date=p_date, type='all')
    outinfo('all: {}'.format(rs))
    save_statistics(obj, rs, collect=True)

    #type==customer
    # customers = Customer.objects.all()
    customers = mails.values_list('customer_id', flat=True).distinct()
    for c in customers:
        rs = get_data(mails.filter(customer_id=c))
        c_all_mails = all_mails.filter(customer_id=c)
        mail_count = c_all_mails.count()
        c_spam_mails = spam_mails.filter(customer_id=c)
        spam_count = c_spam_mails.count()
        spam_rate = (float(spam_count) / float(mail_count)) * 100 if mail_count else 0
        rs.update(mail_count=mail_count, spam_count=spam_count, spam_rate=spam_rate)
        if rs.get('mail_count', 0):
            obj, bool = CStatistics.objects.get_or_create(date=p_date, type='customer', customer_id=c)
            save_statistics(obj, rs, collect=True)
            outinfo('customer({}): {}'.format(c, rs))

def check_error_type(message, flag_list):
    for k in flag_list:
        if re.search(k, message, re.IGNORECASE):
            return True
    return False


def _do_bulk_customer(date):
    print date
    bulk_max = setting.bulk_customer
    # check_list = ['bulk_email', 'error_format', 'recipient_blacklist', 'spam']
    mail_model = get_mail_model(date.strftime('%Y%m%d'))
    # customers = mail_model.objects.filter(check_result__in=check_list).values('customer').annotate(
    #     count=Count("customer")).filter(count__gt=bulk_max).order_by('-count')
    customers = mail_model.objects.filter(state='reject').values('customer').annotate(
        count=Count("customer")).filter(count__gt=bulk_max).order_by('-count')
    print customers
    for c in customers:
        customer = c['customer']
        # sender_dict = mail_model.objects.filter(check_result__in=check_list, customer=customer).values(
        #     'mail_from').annotate(count=Count('mail_from')).order_by('-count')
        sender_dict = mail_model.objects.filter(state='reject', customer=customer).values(
            'mail_from').annotate(count=Count('mail_from')).order_by('-count')
        print sender_dict
        bulk_obj, _ = BulkCustomer.objects.get_or_create(customer_id=customer, date=date)
        bulk_obj.spam_count = c['count']
        bulk_obj.sender_count = len(sender_dict)
        bulk_obj.sender = json.dumps(list(sender_dict))
        bulk_obj.recent_count = BulkCustomer.objects.filter(customer=customer, date__lt=date, date__gt=(date-datetime.timedelta(days=3))).count()
        bulk_obj.save()


def set_bulk_customer():
    """
    判断群发客户
    :return:
    """
    outinfo('set bulk customer start')
    for d in range(0, -1, -1):
        date = datetime.date.today() - datetime.timedelta(days=d)
        _do_bulk_customer(date)
    outinfo('set bulk customer end')


def init_resource():
    global setting

    settings = Settings.objects.all()
    if settings:
        setting = settings[0]

if __name__ == "__main__":
    globals()['_DEBUG'] = Common.check_debug(2)
    Common.init_cfg_default()
    Common.init_run_user(Common.cfgDefault.get('global', 'user'))
    Common.init_pid_file('Statistics.pid')
    Common.init_logger('Statistics', len(sys.argv) > 1, _DEBUG)

    # 获取参数
    if len(sys.argv) >= 2:
        p_date = sys.argv[1]
    elif len(sys.argv) == 1:
        p_date = str(datetime.date.today())
    else:
        outerror("param_error")
        sys.exit(1)

    # 运行程序
    EXIT_CODE = 0
    outinfo("program start")
    init_resource()

    try:
        statistics(p_date)
    except:
        outerror(traceback.format_exc())

    try:
        collect_statistics(p_date)
    except:
        outerror(traceback.format_exc())

    try:
        set_bulk_customer()
    except:
        outerror(traceback.format_exc())
    outinfo("program quit")
    sys.exit(EXIT_CODE)

