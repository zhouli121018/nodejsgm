# coding=utf-8
import datetime
import calendar
from app.statistics.utils import tools as statistics_tools

def get_mail_statistics_time(request, date_type, date_start, date_end, user_id):
    date_type = date_type if date_type in (
        'today', 'yesterday', 'this_week', 'last_week', 'this_month', 'custom', 'subaccount') else 'today'
    customer_id = request.user.id
    today = datetime.date.today()
    fmt = "%Y-%m-%d"
    subobj = None
    if date_type == 'today':
        stat_date_s = stat_date_e = today.strftime(fmt)
    elif date_type == 'yesterday':
        stat_date_s = stat_date_e = (today - datetime.timedelta(days=1)).strftime(fmt)
    elif date_type == 'this_week':
        monday = today - datetime.timedelta(today.weekday())
        sunday = today + datetime.timedelta(6 - today.weekday())
        stat_date_s, stat_date_e = monday.strftime('%Y-%m-%d'), sunday.strftime(fmt)
    elif date_type == 'last_week':
        l_monday = today - datetime.timedelta(today.weekday()+7)
        l_sunday = today - datetime.timedelta(today.weekday()+1)
        stat_date_s, stat_date_e = l_monday.strftime('%Y-%m-%d'), l_sunday.strftime(fmt)
    elif date_type == 'this_month':
        first_day = datetime.date(day=1, month=today.month, year=today.year)
        _, last_day_num = calendar.monthrange(today.year, today.month)
        last_day = datetime.date(day=last_day_num, month=today.month, year=today.year)
        stat_date_s, stat_date_e = first_day.strftime('%Y-%m-%d'), last_day.strftime(fmt)
    elif date_type == 'custom':
        if not date_start:
            date_start = datetime.date(day=1, month=today.month, year=today.year).strftime(fmt)
        if not date_end:
            _, last_day_num = calendar.monthrange(today.year, today.month)
            date_end = datetime.date(day=last_day_num, month=today.month, year=today.year).strftime(fmt)
        stat_date_s, stat_date_e = date_start, date_end
    elif date_type == 'subaccount' and user_id:
        customer_id, subobj = statistics_tools.get_realcustomer_and_obj(request, user_id)
        stat_date_e, stat_date_s = today.strftime(fmt), (today-datetime.timedelta(days=90)).strftime(fmt)
    else:
        stat_date_s = stat_date_e = today.strftime(fmt)
        customer_id = ''
    return customer_id, subobj, stat_date_s, stat_date_e

def mail_statistics_context(request):
    date_type = request.GET.get('date_type', 'today').strip()
    date_start = request.GET.get('date_start', '')
    date_end = request.GET.get('date_end', '')
    user_id  = request.GET.get('user_id', '').strip()
    user_id, subobj, stat_date_s, stat_date_e = get_mail_statistics_time(request, date_type, date_start, date_end, user_id)
    context={
        "subobj": subobj,
        'date_type': date_type,
        'stat_date_s': stat_date_s,
        'stat_date_e': stat_date_e,
        'date_start': date_start,
        'date_end': date_end,
    }
    return context