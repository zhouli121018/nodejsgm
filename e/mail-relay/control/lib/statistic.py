# coding=utf-8
import datetime
import calendar
from django.db.models import Count, Sum
from apps.core.models import CustomerSummary
from apps.mail.models import get_mail_model
from apps.collect_mail.models import get_mail_model as get_mail_model2


# 邮件实际状态和显示给用户的状态不同
STATE_RELATE = {
    'check': 'analysis',
    'review': 'analysis',
    # 'dispatch': 'analysis',
    'bounce': 'fail_finished',
}

def _get_statistic(objs, ctype='relay'):
    if ctype == 'relay':
        res = objs.aggregate(
            total_all=Sum('total_all'),
            all=Sum('all'),
            all_flow=Sum('all_flow'),
            out_all=Sum('out_all'),
            out_all_flow=Sum('out_all_flow'),
            reject=Sum('reject'),
            reject_flow=Sum('reject_flow'),
            finished=Sum('finished'),
            finished_flow=Sum('finished_flow'),
            fail_finished=Sum('fail_finished'),
            fail_finished_flow=Sum('fail_finished_flow'),
        )
    else:
        res = objs.aggregate(
            total_all=Sum('c_total_all'),
            all=Sum('c_all'),
            all_flow=Sum('c_all_flow'),
            out_all=Sum('c_out_all'),
            out_all_flow=Sum('c_out_all_flow'),
            reject=Sum('c_reject'),
            reject_flow=Sum('c_reject_flow'),
            finished=Sum('c_finished'),
            finished_flow=Sum('c_finished_flow'),
            fail_finished=Sum('c_fail_finished'),
            fail_finished_flow=Sum('c_fail_finished_flow'),
        )
    return {
        'total_all': res['total_all'],
        'all': [res['all'], res['all_flow']],
        'out_all': [res['out_all'], res['out_all_flow']],
        'reject': [res['reject'], res['reject_flow']],
        'finished': [res['finished'], res['finished_flow']],
        'fail_finished': [res['fail_finished'], res['fail_finished_flow']]
    }



def get_statistic(customer_id='', date=None, ctype='relay', date_start=None, date_end=None):
    """
    获取一段时间的用户邮件发送状态
    :param ctype:
    :param customer_id:
    :param date:
    :param date_start:
    :param date_end:
    :return:
    """
    if date_start and date_end:
        if isinstance(date_start, basestring):
            date_start = datetime.datetime.strptime(date_start, '%Y-%m-%d')
        if isinstance(date_end, basestring):
            date_end = datetime.datetime.strptime(date_end, '%Y-%m-%d')
        today = datetime.datetime.today()
        if date_start <= today <= date_end:
            obj, _ = CustomerSummary.objects.get_or_create(customer_id=customer_id, date=today)
            save_statistic(obj, ctype)
        objs = CustomerSummary.objects.filter(date__gte=date_start, date__lte=date_end, customer_id=customer_id)
        return _get_statistic(objs, ctype)
    else:
        return get_real_statistic(customer_id, date, ctype)


def get_real_statistic(customer_id='', date=None, ctype='relay'):
    """
    获取用户实时的邮件发送状态
    :param ctype: 客户的类型，relay表示中继，collect表示网关
    :param customer_id: 客户ID
    :param date: 日期
    :return:
    """
    if not date:
        date = datetime.date.today()
    if not isinstance(date, str):
        date = date.strftime('%Y%m%d')

    mail_model = get_mail_model if ctype == 'relay' else get_mail_model2
    model = mail_model(date)

    if customer_id:
        mails = model.objects.filter(customer_id=customer_id)
    else:
        mails = model.objects.all()

    states = mails.values_list("state").annotate(count=Count("id"), size=Sum("size"))
    rs_state = {'finished': [0, 0], 'fail_finished': [0, 0], 'total_all': 0}
    total_count = 0
    total_size = 0
    out_total_count = 0
    out_total_size = 0
    rejects_count = 0
    rejects_size = 0

    for state, count, size in states:
        total_count += count
        total_size += size
        if state in STATE_RELATE:
            state = STATE_RELATE[state]
        if state in ['finished', 'fail_finished']:
            out_total_count += count
            out_total_size += size
        if state in ['reject', 'c_reject']:
            rejects_count += count
            rejects_size += size
        if state in rs_state:
            rs_state[state][0] += count
            rs_state[state][1] += size
        else:
            rs_state[state] = [count, size]
    rs_state['all'] = [total_count, total_size]
    rs_state['out_all'] = [out_total_count, out_total_size]
    rs_state['total_all'] = mails.filter(mail_id=0).count()
    rs_state['reject'] = [rejects_count, rejects_size]
    return rs_state


def save_statistic(summary_obj, ctype='relay'):
    """
    获取用户实时的邮件发送状态, 并保存到数据库CustomerSummary中
    :param ctype:
    :param customer_summary_obj:
    :return:
    """
    fields = ['all', 'out_all', 'reject', 'finished', 'fail_finished', 'total_all']
    res = get_real_statistic(summary_obj.customer.id, summary_obj.date, ctype)
    for f in fields:
        r = res.get(f, 0)
        if not r:
            continue
        if ctype == 'collect':
            f = 'c_{}'.format(f)
        if f.endswith('total_all'):
            setattr(summary_obj, f, r)
        else:
            setattr(summary_obj, f, r[0])
            setattr(summary_obj, '{}_flow'.format(f), r[1])
    summary_obj.save()

def get_summary_statistic(customer_id='', ctype='relay', stype='day', date_start=None, date_end=None):
    """
    获取一段时间的用户邮件发送状态
    :param customer_id:
    :param ctype: relay or collect
    :param stype: day or week or month
    :param date_start:
    :param date_end:
    :return:
    """

    date_start_tmp = date_start
    res = []
    while date_start_tmp <= date_end:
        date_end_tmp = date_start_tmp
        if stype == 'week':
            while date_end_tmp.weekday() != 6 and date_end_tmp < date_end:
                date_end_tmp = date_end_tmp + datetime.timedelta(days=1)
            key = "{} -- {}".format(date_start_tmp.strftime('%Y-%m-%d'), date_end_tmp.strftime('%Y-%m-%d'))
        elif stype == 'month':
            while date_end_tmp.day != calendar.monthrange(date_start_tmp.year, date_start_tmp.month)[1] and date_end_tmp < date_end:
                date_end_tmp = date_end_tmp + datetime.timedelta(days=1)
            key = date_start_tmp.strftime('%Y-%m')
        else:
            key = date_start_tmp.strftime('%Y-%m-%d')

        _res = get_statistic(customer_id=customer_id, ctype=ctype, date_start=date_start_tmp, date_end=date_end_tmp)
        _res['key'] = key
        _res['date_start'] = date_start_tmp
        _res['date_end'] = date_end_tmp
        if _res['total_all']:
            res.append(_res)
        date_start_tmp = date_end_tmp + datetime.timedelta(days=1)
    res.reverse()
    return res
