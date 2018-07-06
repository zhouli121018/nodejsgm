# coding=utf-8
import sys
import datetime
from django.db import connections
from django.core.cache import cache
from django.db.models import Sum, Max, Min
from app.track.models import TrackStat, StatTask
from app.task.models import SendContent, SendTask
from app.track.utils import tools

###################################################
# 通过 open_first、open_last 获取区间打开点击数
# 打开开始时间为准，2天之内的以2个小时为界限，之后的以天为界限，最多显示10天的
def get_invarl_track(key, track_stats, user_id, open_first, open_last, click_first, click_last):
    if not open_first and not click_first:
        raise Exception("no data")
    if click_first and click_first<open_first:
        open_first = click_first
    if not open_last:
        open_last = open_first
    if click_last and click_last>open_last:
        open_last = click_last
    div_times = (open_last-open_first).total_seconds()
    cache_flags = True if div_times>3*60*60 else False
    track_intervals = cache.get(key, None)
    if track_intervals:
        return ( cache_flags, track_intervals['track_interval_times'],
                 track_intervals['track_interval_opens'],
                 track_intervals['track_interval_clicks'])
    open_first = datetime.datetime.strptime(open_first.strftime('%Y-%m-%d %H:00:00'), "%Y-%m-%d %H:%M:%S")
    track_ids = track_stats.values_list('id', flat=True)
    open_tablename = '{}_track_email'.format(user_id)
    click_tablename = '{}_track_click'.format(user_id)
    track_interval_times = []
    track_interval_opens = []
    track_interval_clicks = []

    cr = connections['mm-track'].cursor()
    open_first_after_2 = open_first + datetime.timedelta(days=2)
    open_first_after_10 = open_first + datetime.timedelta(days=10)
    where_str = u' track_id in ({})'.format(','.join(map(str, track_ids)))
    hours = 2
    if div_times<=24*60*60:
        hours = 1
    while open_first<=open_last:
        if open_first<open_first_after_2:
            open_first_tmp = open_first + datetime.timedelta(hours=hours)
            s = open_first.strftime('%Y-%m-%d %Hh')
        else:
            open_first_tmp = open_first + datetime.timedelta(days=1)
            s = open_first.strftime('%Y-%m-%d')

        if open_first_tmp>=open_first_after_10:
            open_sql = "SELECT sum(open_total) FROM {} WHERE open_first>=%s AND {}".format(open_tablename, where_str)
            click_sql = "SELECT sum(click_total) FROM {} WHERE click_first>=%s AND {}".format(click_tablename, where_str)
            args = (open_first,)
        else:
            open_sql = "SELECT sum(open_total) FROM {} WHERE open_first>=%s AND open_first<%s AND {}".format(open_tablename, where_str)
            click_sql = "SELECT sum(click_total) FROM {} WHERE click_first>=%s AND click_first<%s AND {}".format(click_tablename, where_str)
            args = (open_first, open_first_tmp)
        # 唯一 sum(open_total) 改为 count(*)
        # print>> sys.stderr, open_sql, args

        cr.execute(open_sql, args)
        rows = cr.fetchall()
        open_count = rows and rows[0][0] or 0

        # 唯一 sum(click_total) 改为 sum(click_unique)
        cr.execute(click_sql, args)
        rows = cr.fetchall()
        click_count = rows and rows[0][0] or 0
        # if open_count or click_count:
        track_interval_times.append(s)
        track_interval_opens.append(int(open_count))
        track_interval_clicks.append(int(click_count))
        open_first = open_first_tmp
        if open_first>open_first_after_10:
            break
    d = {
        "track_interval_times": track_interval_times,
        "track_interval_opens": track_interval_opens,
        "track_interval_clicks": track_interval_clicks
    }
    cache.set(key, d, 60)
    return cache_flags, track_interval_times, track_interval_opens, track_interval_clicks

# 获取 邮件跟踪的 context
def get_track_context(request):
    user_id = request.user.id
    ident = request.GET.get('ident', '')
    content_id = request.GET.get('content_id', '')
    key = ":django:edmweb:track:track_task:trak:{user_id}:{ident}:{content_id}:open:".format(
        user_id=user_id, ident=ident, content_id=content_id)
    key2 = ":django:edmweb:track:track_task:trak:{user_id}:{ident}:{content_id}:ctx:".format(
        user_id=user_id, ident=ident, content_id=content_id)
    context = cache.get(key2, None)
    if not context:
        # 取得任务跟踪ID
        track_stats = TrackStat.objects.filter(task_ident=ident, customer_id=user_id)
        if content_id:
            track_stats = track_stats.filter(content_id=content_id)
        track_stat = track_stats.aggregate(open_total=Sum('open_total'), open_unique=Sum('open_unique'),
                                           open_first=Min('open_first'), open_last=Max('open_last'),
                                           click_total=Sum('click_total'), click_unique=Sum('click_unique'),
                                           click_first=Min('click_first'), click_last=Max('click_last'))

        # 取得任务实际发送量
        value = StatTask.objects.filter(customer_id=user_id, task_ident=ident).aggregate(count_send=Sum('count_send'),
                                                                                         count_error=Sum('count_error'))
        count_send = value['count_send'] or 0
        count_error = value['count_error'] and int(value['count_error']) or 0
        count_succes = count_send - count_error
        # 取得任务发送的开始、结束日期
        date_list = list(
            StatTask.objects.filter(task_ident=ident).values_list('task_date', flat=True).order_by('task_date'))

        task_date_first = date_list[0]
        task_date_last = date_list[-1]

        # 打开率、 点击率
        open_total = int(track_stat.get('open_total', 0))
        open_unique = int(track_stat.get('open_unique', 0))
        click_total = int(track_stat.get('click_total', 0))
        click_unique = int(track_stat.get('click_unique', 0))

        open_first = track_stat['open_first']
        open_last = track_stat['open_last']
        click_first = track_stat['click_first']
        click_last = track_stat['click_last']

        cache_flags, track_interval_times, track_interval_opens, track_interval_clicks = get_invarl_track(
            key, track_stats, user_id, open_first, open_last, click_first, click_last)
        show_stat_rate = tools.get_rate(open_unique, count_succes)
        show_link_rate = tools.get_rate(click_unique, open_unique)

        data_list = [count_send, count_error, count_succes, open_unique, open_total, click_unique, click_total]
        max_length = len(data_list)
        data_list.sort()
        max_data = tools.get_max_data(data_list[-1])
        context={
            'ident': ident,
            'count_send': count_send,
            'count_error': count_error,
            'count_succes': count_succes,
            'open_total': open_total,
            'open_unique': open_unique,
            'click_total': click_total,
            'click_unique': click_unique,
            'open_first': open_first,
            'open_last': open_last,
            'click_first': click_first,
            'click_last': click_last,
            'task_date_first': task_date_first,
            'task_date_last': task_date_last,
            'show_stat_rate': show_stat_rate,
            'show_link_rate': show_link_rate,

            'max_data': max_data,
            'max_length': max_length,
            'track_stats': track_stats,
            'content_id': content_id,
            'is_mutil_template': SendContent.objects.filter(send__send_name=ident).count() > 1 and not content_id,

            'track_interval_times': track_interval_times,
            'track_interval_opens': track_interval_opens,
            'track_interval_clicks': track_interval_clicks,
        }
        if cache_flags:
            cache.set(key2, context, 600)
    return context
