# coding=utf-8
import re
import json
from django.template.response import TemplateResponse
from django.http import Http404, HttpResponse
from django.utils.translation import ugettext_lazy as _
from app.statistics.utils import sqls as statistics_sqls, contexts as statistics_contexts
from lib.excel_response import ExcelResponse, DHeadExcelResponse, MultiSheetExcelResponse
from app.statistics.utils import tools as statistics_tools
from django.core.cache import cache
from django.db import connections
from django.db.models import Sum, Max
from app.task.models import SendTask
from app.track.models import StatTask, TrackStat, TrackLink, StatError
from lib.common import get_object
from lib.IpSearch import IpSearch
from app.statistics.configs import DATA_TYPES, AREA_CODE, COLOR_20, JC_CODE_COUNTRY, ERRTYPE_VALS

def ajax_mail_statistics(request):
    data = request.GET
    date_type = request.GET.get('date_type', 'today').strip()
    date_start = request.GET.get('date_start', '')
    date_end = request.GET.get('date_end', '')
    sub_user_id  = request.GET.get('user_id', '').strip()
    user_id, subobj, stat_date_s, stat_date_e = statistics_contexts.get_mail_statistics_time(request, date_type, date_start, date_end, sub_user_id)
    key = ":django:edmweb:subaccount:ajax_mail_statistics:statistics:{user_id}:{date_start}:{date_end}:{date_type}:".format(
        user_id=user_id,
        date_start=stat_date_s.replace("-", ""),
        date_end=stat_date_e.replace("-", ""),
        date_type=date_type
    )
    content = cache.get(key, None)
    if not content:
        order_column = data.get('order[0][column]', '')
        order_dir = data.get('order[0][dir]', '')
        search = data.get('search[value]', '')

        cr = connections['mm-ms'].cursor()
        sql = u'''
        SELECT COUNT(DISTINCT task_date) FROM stat_task
        WHERE customer_id={0} AND task_date BETWEEN '{1}' AND '{2}'
        '''.format(user_id, stat_date_s, stat_date_e)
        cr.execute(sql)
        rows = cr.fetchall()
        count = rows[0][0]
        try:
            length = int(data.get('length', 1))
        except ValueError:
            length = 1
        try:
            start_num = int(data.get('start', '0'))
        except ValueError:
            start_num = 0

        colums = ['stat.task_date', 'core.company']
        if order_column and int(order_column) < len(colums):
            if order_dir == 'desc':
                order_by_str = u' order by %s desc' % colums[int(order_column)]
            else:
                order_by_str = u' order by %s asc' % colums[int(order_column)]
        else:
            order_by_str = u' order by stat.task_date desc'
        sql = statistics_sqls.get_statistics_sql(user_id, stat_date_s, stat_date_e, order_by_str)
        limit_sql = u'LIMIT {} OFFSET {}'.format(length, start_num)
        sql += limit_sql
        cr.execute(sql)
        desc = cr.description
        rows = cr.fetchall()
        rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
        re_str = '<td.*?>(.*?)</td>'
        field = [col[0] for col in desc]
        for d in rows:
            t = TemplateResponse(request, 'statistics/ajax_mail_statistics.html', {
                'd': dict(zip(field, d)), 'subobj': subobj, })
            t.render()
            rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        content = HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")
        cache.set(key, content, 300)
    return content

def mail_statistics_export(user_id, date_start, date_end):
    key = ":django:edmweb:subaccount:mail_statistics_export:statistics:{user_id}:{date_start}:{date_end}:".format(
        user_id=user_id,
        date_start=date_start.replace("-", ""),
        date_end=date_end.replace("-", ""),
    )
    content = cache.get(key, None)
    if not content:
        order_by_str = u' order by stat.task_date desc'
        sql = statistics_sqls.get_statistics_sql(user_id, date_start, date_end, order_by_str)
        cr = connections['mm-ms'].cursor()
        cr.execute(sql)
        rows = cr.fetchall()
        lists = []
        (r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11)=(0,0,0,0,0,0,0,0,0,0,0)
        for r in rows:
            ( username, task_date, company, count_send, count_error, count_succes, error_type_9,
              error_type_8, count_send_exp, point_exp, count_send_real, count_fail, count_err_5, point_real ) = r
            r1+=count_send
            r2+=count_error
            r3+=count_succes
            r4+=error_type_9
            r5+=error_type_8
            r6+=count_send_exp
            r7+=point_exp
            r8+=count_send_real
            r9+=count_fail
            r10+=count_err_5
            r11+=point_real
            count_send = count_send if count_send else '-'
            count_error = count_error if count_error else '-'
            count_succes = count_succes if count_succes else '-'
            error_type_9 = error_type_9 if error_type_9 else '-'
            error_type_8 = error_type_8 if error_type_8 else '-'
            count_send_exp = count_send_exp if count_send_exp else '-'
            point_exp = point_exp if point_exp else '-'
            count_send_real = count_send_real if count_send_real else '-'
            count_fail = count_fail if count_fail else '-'
            count_err_5 = count_err_5 if count_err_5 else '-'
            point_real = point_real if point_real else '-'
            lists.append([
                task_date, u'{}（{}）'.format(company, username), count_send, count_error, count_succes,
                error_type_9, error_type_8, count_send_exp, point_exp, count_send_real, count_fail, count_err_5, point_real
            ])
        header = [
            [_(u'日期'), (0, 1, 0, 0), []],
            [_(u'客户名称'), (0, 1, 1, 1), []],
            [_(u'Web发送量统计'), (0, 0, 2, 4), [ [_(u'任务量'),(1, 2)], [_(u'失败量'),(1, 3)], [_(u'发送量'),(1, 4)]]],
            [_(u'错误地址'), (0, 0, 5, 6), [[_(u'格式错误'),(1, 5)], [_(u'无效地址'),(1, 6)]]],
            [_(u'预统计/扣点'), (0, 0, 7, 8), [[_(u'发送量'),(1, 7)], [_(u'预扣点'),(1, 8)]]],
            [_(u'实际统计/扣点'), (0, 0, 9, 12), [[_(u'实际发送'),(1, 9)], [_(u'投递失败'),(1, 10)], [_(u'拒绝投递'),(1, 11)], [_(u'实际扣点'),(1, 12)]]],
        ]

        footer = []
        if rows:
            footer_row = len(rows) + 2
            footer = [_(u'总计：'), (footer_row, footer_row, 0, 1), [
                [r1,(footer_row, 2)], [r2,(footer_row, 3)], [r3,(footer_row, 4)], [r4,(footer_row, 5)], [r5,(footer_row, 6)],
                [r6,(footer_row, 7)], [r7,(footer_row, 8)], [r8,(footer_row, 9)], [r9,(footer_row, 10)], [r10,(footer_row, 11)], [r11,(footer_row, 12)]
            ]]
        if date_start == date_end:
            output_name=u'{}'.format(date_start)
        else:
            output_name = u'{}{}{}'.format(date_start, _(u'至'),date_end)
        content = DHeadExcelResponse(
            data=lists,
            output_name=output_name,
            headers=header,
            footer=footer,
            encoding='gbk'
        )
        cache.set(key, content, 300)
    return content

def ajax_batch_statistics(request):
    data = request.GET
    date_start = data.get('date_start', '')
    date_end = data.get('date_end', '')
    user_id  = data.get('user_id', '').strip()
    customer_id, subobj = statistics_tools.get_realcustomer_and_obj(request, user_id)
    key = ":django:edmweb:subaccount:ajax_batch_statistics:batch:{user_id}:{date_start}:{date_end}:".format(
        user_id=customer_id,
        date_start=date_start.replace("-", ""),
        date_end=date_end.replace("-", ""),
    )
    content = cache.get(key, None)
    if not content:
        order_column = data.get('order[0][column]', '')
        order_dir = data.get('order[0][dir]', '')
        search = data.get('search[value]', '')
        cr = connections['mm-ms'].cursor()
        sql = u'''
        SELECT COUNT(DISTINCT task_ident) FROM stat_task
        WHERE customer_id={0} AND task_date BETWEEN '{1}' AND '{2}'
        '''.format(customer_id, date_start, date_end)
        cr.execute(sql)
        rows = cr.fetchall()
        count = rows[0][0] if rows[0][0] else 0

        try:
            length = int(data.get('length', 1))
        except ValueError:
            length = 1

        try:
            start_num = int(data.get('start', '0'))
        except ValueError:
            start_num = 0

        colums = ['stat.task_date', 'stat.task_ident', 'core.company']
        if order_column and int(order_column) < len(colums):
            if order_dir == 'desc':
                order_by_str = u' order by %s desc' % colums[int(order_column)]
            else:
                order_by_str = u' order by %s asc' % colums[int(order_column)]
        else:
            order_by_str = u' order by stat.task_date desc'

        sql = u'''
        SELECT core.customer_id, core.username, core.company,
                stat.task_date, stat.task_ident, stat.task_id,
                CAST(stat.count_send_exp AS SIGNED) AS count_send_exp,
                CAST(stat.count_send_real AS SIGNED) AS count_send_real,
                CAST(stat.count_fail AS SIGNED) AS count_fail,

                CAST(stat.count_err_1 AS SIGNED) AS count_err_1,
                CAST(stat.count_err_2 AS SIGNED) AS count_err_2,
                CAST(stat.count_err_3 AS SIGNED) AS count_err_3,
                CAST(stat.count_err_5 AS SIGNED) AS count_err_5,

                task.send_maillist, task.send_id
        FROM (
             SELECT customer_id, username, company FROM core_customer WHERE customer_id={0}
        ) core
        LEFT JOIN (
            SELECT customer_id, task_date, task_ident, task_id,
                    SUM(count_send) - SUM(count_error) + SUM(count_err_1) + SUM(count_err_2) + SUM(count_err_3) + SUM(count_err_5) AS count_send_exp, -- 发送量
                    SUM(count_send) - SUM(count_error) AS count_send_real, -- 实际发送
                    SUM(count_err_1) + SUM(count_err_2) + SUM(count_err_3) AS count_fail,-- 投递失败

                    SUM(count_err_1) AS count_err_1,   -- 邮箱不存在
                    SUM(count_err_2) AS count_err_2,   -- 空间不足
                    SUM(count_err_3) AS count_err_3,   -- 用户拒收
                    SUM(count_err_5) AS count_err_5    -- 拒绝投递
            FROM stat_task
            WHERE customer_id={0} AND task_date BETWEEN '{1}' AND '{2}'
            GROUP BY customer_id, task_date, task_ident, task_id
        ) stat ON stat.customer_id = core.customer_id
        LEFT JOIN (
            SELECT user_id AS customer_id, send_id, send_name, send_maillist
            FROM ms_send_list
            WHERE user_id={0} AND send_time BETWEEN '{1} 00:00:00' AND '{2} 23:59:59'
        ) task ON task.customer_id = stat.customer_id AND task.send_name = stat.task_ident
        WHERE stat.customer_id IS NOT NULL
       {5} LIMIT {3} OFFSET {4};
        '''.format(customer_id, date_start, date_end, length, start_num, order_by_str)
        cr.execute(sql)
        desc = cr.description
        rows = cr.fetchall()
        rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
        re_str = '<td.*?>(.*?)</td>'
        field = [col[0] for col in desc]
        for d in rows:
            t = TemplateResponse(request, 'statistics/ajax_batch_statistics.html', { 'd': dict(zip(field, d)), "subobj": subobj, })
            t.render()
            rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        content = HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")
        cache.set(key, content, 300)
    return content

def ajax_sender_statistics(request):
    data = request.GET
    date_start = data.get('date_start', '')
    date_end = data.get('date_end', '')
    user_id  = data.get('user_id', '').strip()
    customer_id, subobj = statistics_tools.get_realcustomer_and_obj(request, user_id)
    key = ":django:edmweb:subaccount:ajax_sender_statistics:sender:{user_id}:{date_start}:{date_end}:".format(
        user_id=customer_id,
        date_start=date_start.replace("-", ""),
        date_end=date_end.replace("-", ""),
    )
    content = cache.get(key, None)
    if not content:
        order_column = data.get('order[0][column]', '')
        order_dir = data.get('order[0][dir]', '')
        search = data.get('search[value]', '')
        cr = connections['mm-ms'].cursor()
        sql = u'''
        SELECT COUNT(DISTINCT sender) FROM stat_sender
        WHERE customer_id={0} AND date BETWEEN '{1}' AND '{2}'
        '''.format(customer_id, date_start, date_end)
        cr.execute(sql)
        rows = cr.fetchall()
        count = rows[0][0] if rows[0][0] else 0

        try:
            length = int(data.get('length', 1))
        except ValueError:
            length = 1

        try:
            start_num = int(data.get('start', '0'))
        except ValueError:
            start_num = 0

        order_by_str = ''
        colums = ['stat.task_date', 'core.company', 'stat.sender',  'stat.send_count', 'stat.lastip']
        if order_column and int(order_column) < len(colums):
            if order_dir == 'desc':
                order_by_str = u'order by %s desc' % colums[int(order_column)]
            else:
                order_by_str = u'order by %s asc' % colums[int(order_column)]

        sql = u'''
        SELECT core.customer_id, core.username, core.company,
                stat.task_date, stat.sender,
                stat.send_count, stat.lastip
        FROM (
             SELECT customer_id, username, company FROM core_customer WHERE customer_id={0}
        ) core
        LEFT JOIN (
            SELECT s.customer_id, s.date AS task_date, s.sender,
                    SUM(s.count) AS send_count,   -- 发送数量
                    s.lastip
            FROM stat_sender AS s
            WHERE s.customer_id={0} AND s.date BETWEEN '{1}' AND '{2}'
            GROUP BY s.customer_id, s.date, s.sender, s.lastip
        ) stat ON stat.customer_id = core.customer_id
        WHERE stat.customer_id IS NOT NULL
        {5} LIMIT {3} OFFSET {4};
        '''.format(customer_id, date_start, date_end, length, start_num, order_by_str)
        cr.execute(sql)
        desc = cr.description
        rows = cr.fetchall()
        rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
        re_str = '<td.*?>(.*?)</td>'
        field = [col[0] for col in desc]
        for d in rows:
            t = TemplateResponse(request, 'statistics/ajax_sender_statistics.html', { 'd': dict(zip(field, d)) })
            t.render()
            rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        content = HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")
        cache.set(key, content, 300)
    return content

def mail_statistics_report_context(request, task_id):
    key = ":django:edmweb:statistics:mail_statistics_report:report:task_id:{task_id}:".format(
        task_id=task_id)
    # context = cache.get(key, None)
    context = None
    if not context:
        obj = get_object(SendTask, request.user, task_id)
        # if obj.send_status != 3:
        #     raise Http404
        # 任务发送数
        task_send_total = obj.get_real_send_qty()

        # 取得任务实际发送量
        value = StatTask.objects.filter(customer_id=request.user.id, task_ident=obj.send_name).aggregate(
            count_send=Sum('count_send'), count_error=Sum('count_error'),
            count_err_1=Sum('count_err_1'), count_err_2=Sum('count_err_2'),
            count_err_3=Sum('count_err_3'), count_err_5=Sum('count_err_5'),
        )
        count_send = value['count_send'] if value['count_send'] else 0
        count_error = int(value['count_error']) if value['count_error'] else 0 # 发送失败
        count_succes = count_send - count_error    # 发送成功数

        # 格式错误、无效
        # count_invalid = send_total - count_send
        # -------------------
        # 格式错误、无效
        count_invalid = obj.error_count
        # 一共发送数
        send_total = count_send + count_invalid
        # -------------------

        # 邮箱不存在
        count_err_1 = value['count_err_1'] if value['count_err_1'] else 0
        # 空间不足
        count_err_2 = value['count_err_2'] if value['count_err_2'] else 0
        # 用户拒收
        count_err_3 = value['count_err_3'] if value['count_err_3'] else 0
        # 垃圾拒绝发送
        count_err_5 = value['count_err_5'] if value['count_err_5'] else 0
        total_error = count_invalid + count_err_1 + count_err_2 + count_err_3 + count_err_5

        # 邮件打开
        stat_objs = TrackStat.objects.filter(task_ident=obj.send_name, customer_id=request.user.id)

        stat_obj = stat_objs[0] if stat_objs else None


        show_stat_rate, show_link_rate, show_link_rate_suc = '0%', '0%',  '0%'

        # 浏览器、操作系统、 地域 点击链接 统计
        link_objs = None
        ip_search = IpSearch()
        browser_count = {'ie': 0, 'firefox': 0, 'chrome': 0, 'other': 0}
        os_count = {'windows': 0, 'linux': 0, 'macintosh': 0, 'other': 0}
        area_list, area_lists, country_list, country_lists = [], {}, [], {}
        domain_data_click, domain_data_all = [], []
        pattern ='([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])'
        ip_compile = re.compile(pattern)
        track_stat = stat_objs.aggregate(open_total=Sum('open_total'), open_unique=Sum('open_unique'),
                                         click_total=Sum('click_total'), click_unique=Sum('click_unique'))
        open_total = track_stat['open_total'] or 0
        open_unique = track_stat['open_unique'] or 0
        click_total = track_stat['click_total'] or 0
        click_unique = track_stat['click_unique'] or 0
        if stat_objs:
            track_ids = stat_objs.values_list('id', flat=True)

            # open_total = stat_obj.open_total
            show_stat_rate = statistics_tools.get_rate(open_unique, count_succes)
            show_link_rate = statistics_tools.get_rate(click_unique, open_unique)
            show_link_rate_suc = statistics_tools.get_rate(click_unique, count_succes)

            link_objs = TrackLink.objects.filter(track_id__in=track_ids).exists()

            cr = connections['mm-track'].cursor()
            tablename = '{}_track_email'.format(request.user.id)

            sql = u""" SELECT email FROM {0} WHERE track_id in ({1}) AND click_total > 0; """.format(tablename, ','.join(map(lambda s: str(s), track_ids)))
            cr.execute(sql)
            domain_data_click = statistics_tools.get_domain_data(cr.fetchall())

            sql = u""" SELECT email FROM {0} WHERE track_id in ({1}) AND open_total > 0; """.format(tablename, ','.join(map(lambda s: str(s), track_ids)))
            cr.execute(sql)
            domain_data_all = statistics_tools.get_domain_data(cr.fetchall())


            # 地域分布
            sql = u"""
            SELECT browser, os, ip_first, ip_last, open_total, click_total, email
            FROM {0} WHERE track_id in ({1});
            """.format(tablename, ','.join(map(lambda s: str(s), track_ids)))
            cr.execute(sql)
            rows = cr.fetchall()

            for row in rows:
                if row[0].lower().startswith('msie') or row[0].lower().startswith('ie'):
                    browser_count['ie'] += 1
                elif row[0].lower().startswith('firefox'):
                    browser_count['firefox'] += 1
                elif row[0].lower().startswith('chrome'):
                    browser_count['chrome'] += 1
                else:
                    browser_count['other'] += 1

                if row[1].lower().startswith('windows'):
                    os_count['windows'] += 1
                elif row[1].lower().startswith('linux'):
                    os_count['linux'] += 1
                elif row[1].lower().startswith('mac'):
                    os_count['macintosh'] += 1
                else:
                    os_count['other'] += 1

                ip = ''
                if row[2]:
                    ip = row[2]
                elif row[3]:
                    ip = row[3]
                if not ip:
                    continue

                m = ip_compile.search(ip)
                if m:
                    ip = m.group(0)
                else:
                    continue

                ip_info = ip_search.Find(ip)
                country, area = statistics_tools.split_ip_info(ip_info)
                if not country:
                    continue
                if country not in country_list:
                    country_list.append(country)
                    country_lists.update({ country: [row[4], 1] })
                else:
                    country_lists.update({
                        country: [
                            country_lists[country][0] + row[4],
                            country_lists[country][1] + 1,
                            ]
                    })

                if not area:
                    continue

                if area not in area_list:
                    area_list.append(area)
                    area_lists.update({ area: [row[4], 1] })
                else:
                    area_lists.update({
                        area: [
                            area_lists[area][0] + row[4],
                            area_lists[area][1] + 1,
                            ]
                    })

        area_sort_tmp = sorted(area_lists.items(),key=lambda e:e[1][0], reverse=True)[:10]
        country_sort_tmp = sorted(country_lists.items(),key=lambda e:e[1][0], reverse=True)[:10]
        area_data, country_data = {}, {}
        area_sort, country_sort = [], []
        for d in area_sort_tmp:
            if d[0] in AREA_CODE.keys():
                area_data.update({
                    AREA_CODE[d[0]]: int(d[1][0]),
                })
            area_sort.append(
                (d[0], int(d[1][0]), int(d[1][1]))
            )
        for d in country_sort_tmp:
            if d[0] in JC_CODE_COUNTRY:
                country_data.update({
                    JC_CODE_COUNTRY[d[0]]: int(d[1][0]),
                })
            country_sort.append(
                (d[0], int(d[1][0]), int(d[1][1]))
            )
        area_max = statistics_tools.get_gfc_max_data(area_sort_tmp[0][1][0]) if area_sort_tmp else 5000
        country_max = statistics_tools.get_gfc_max_data(country_sort_tmp[0][1][0]) if area_sort_tmp else 5000
        context = {
            'task_obj': obj,
            'task_id': task_id,
            'task_send_total': task_send_total,
            'send_total': send_total,
            'count_send': count_send,
            'count_succes': count_succes,
            'count_succes_rate': statistics_tools.get_rate(count_succes, count_send - count_err_5),
            'real_count_send': count_send-count_err_5,
            'real_count_error': count_error - count_err_5,

            'count_error': count_error,
            'count_error_rate': statistics_tools.get_rate(count_error - count_err_5, count_send - count_err_5),

            'total_error': total_error,
            'count_invalid': {'value': count_invalid, 'width':  statistics_tools.get_width(count_invalid, total_error), 'rate': statistics_tools.get_rate(count_invalid, total_error)},
            'count_err_1': {'value': count_err_1, 'width':  statistics_tools.get_width(count_err_1, total_error), 'rate': statistics_tools.get_rate(count_err_1, total_error)},
            'count_err_2': {'value': count_err_2, 'width':  statistics_tools.get_width(count_err_2, total_error), 'rate': statistics_tools.get_rate(count_err_2, total_error)},
            'count_err_3': {'value': count_err_3, 'width':  statistics_tools.get_width(count_err_3, total_error), 'rate': statistics_tools.get_rate(count_err_3, total_error)},
            'count_err_5': {'value': count_err_5, 'width':  statistics_tools.get_width(count_err_5, total_error), 'rate': statistics_tools.get_rate(count_err_5, total_error)},

            'stat_objs': stat_objs,
            'show_stat_rate': show_stat_rate,
            'open_total': open_total,
            'open_unique': open_unique,
            'open_unique_rate': statistics_tools.get_rate(open_unique, count_succes),
            'no_open': count_succes - open_unique,
            'no_open_rate': statistics_tools.get_rate(count_succes - open_unique, count_succes),
            'click_total': click_total,
            'click_unique': click_unique,
            'show_link_rate': show_link_rate,
            'show_link_rate_suc': show_link_rate_suc,
            'no_click': count_succes - click_unique,
            'no_click_rate': statistics_tools.get_rate(count_succes - click_unique, count_succes),

            'link_objs': link_objs,
            'domain_data_click': domain_data_click,
            'domain_data_all': domain_data_all,

            'area_sort': area_sort,
            'country_sort': country_sort,
            'area_data': area_data,
            'country_data': country_data,
            'area_max': area_max,
            'country_max':country_max,
            'os_count': os_count,
            'browser_count': browser_count,
        }
        # cache.set(key, context, 300)
    return context

def track_task_pdf_context(request):
    data = request.GET
    ident = data.get('ident', '')
    mode = data.get('mode', '')
    user_id = request.user.id
    # key = ":django:edmweb:statistics:track_task_pdf_context:report:{ident}:{user_id}:".format(
    #     user_id=user_id,
    #     ident=ident)
    # context = cache.get(key, None)
    context = None
    if not context:
        # 取得任务跟踪ID
        stat_objs = TrackStat.objects.filter(task_ident=ident, customer_id=user_id)
        task_objs = SendTask.objects.filter(send_name=ident, user_id=user_id)
        track_status = task_objs[0].track_status
        stat_obj = stat_objs[0]
        track_id = stat_obj.id
        # 取得任务实际发送量
        value = StatTask.objects.filter(customer_id=user_id, task_ident=ident).aggregate(count_send=Sum('count_send'), count_error=Sum('count_error'))
        count_send = value['count_send']
        count_error = int(value['count_error'])
        count_succes = count_send - count_error
        # 取得任务发送的开始、结束日期
        date_list = list(StatTask.objects.filter(task_ident=ident).values_list('task_date', flat=True).order_by('task_date'))
        task_date_first = date_list[0]
        task_date_last = date_list[-1]
        #打开率、 点击率
        open_total = stat_obj.open_total
        open_unique = stat_obj.open_unique
        click_total = stat_obj.click_total
        click_unique = stat_obj.click_unique
        open_first = stat_obj.open_first
        open_last = stat_obj.open_last
        click_first = stat_obj.click_first
        click_last = stat_obj.click_last
        open_total = int(open_total) if open_total else 0
        open_unique = int(open_unique) if open_unique else 0
        click_total = int(click_total) if click_total else 0
        click_unique = int(click_unique) if click_unique else 0
        show_stat_rate = statistics_tools.get_rate(open_unique, count_succes)
        show_link_rate = statistics_tools.get_rate(click_unique, open_unique)

        link_objs = TrackLink.objects.filter(track_id=track_id).order_by('-click_unique', '-click_total')[:50]
        data_list = [count_send, count_error, count_succes, open_unique, open_total, click_unique, click_total]
        histogram_x_width = '14.2857%'

        data_list.sort()
        max_data = statistics_tools.get_max_data(data_list[-1])
        histogram_x_list = [1,2,3,4,5,6]
        histogram_y_list = statistics_tools.get_histogram_y_list(max_data)
        histogram_y_list.sort(reverse=True)
        context={
            'pagesize': 'A4',
            'ident': ident,
            'track_id': track_id,
            'track_status': track_status,
            'count_send': count_send,
            'count_error':count_error,
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

            'stat_obj': stat_obj,
            'link_objs': link_objs,

            'histogram_x_width': histogram_x_width,
            'histogram_x_list': histogram_x_list,
            'histogram_y_list': histogram_y_list,

            'count_send_height_rate': statistics_tools.get_rate(count_send, max_data, 4),
            'count_succes_height_rate': statistics_tools.get_rate(count_succes, max_data, 4),
            'count_error_height_rate': statistics_tools.get_rate(count_error, max_data, 4),
            'open_unique_height_rate': statistics_tools.get_rate(open_unique, max_data, 4),
            'open_total_height_rate': statistics_tools.get_rate(open_total, max_data, 4),
            'click_unique_height_rate': statistics_tools.get_rate(click_unique, max_data, 4),
            'click_total_height_rate': statistics_tools.get_rate(click_total, max_data, 4),

            "filename": u"{}.pdf".format(ident),
        }
        # cache.set(key, context, 300)
    return context

def mail_statistics_report_pdf_context(request, task_id):
    # key = ":django:edmweb:statistics:mail_statistics_report_pdf_context:report:{task_id}:".format(
    #     task_id=task_id)
    # context = cache.get(key, None)
    context = None
    if not context:
        obj = get_object(SendTask, request.user, task_id)
        if obj.send_status != 3:
            raise Http404
        # 任务发送数
        task_send_total = obj.get_real_send_qty()

        # 取得任务实际发送量
        value = StatTask.objects.filter(customer_id=request.user.id, task_ident=obj.send_name).aggregate(
            count_send=Sum('count_send'), count_error=Sum('count_error'),
            count_err_1=Sum('count_err_1'), count_err_2=Sum('count_err_2'),
            count_err_3=Sum('count_err_3'), count_err_5=Sum('count_err_5'),
        )
        count_send = value['count_send'] if value['count_send'] else 0
        count_error = int(value['count_error']) if value['count_error'] else 0 # 发送失败
        count_succes = count_send - count_error    # 发送成功数

        # 格式错误、无效
        # count_invalid = send_total - count_send
        # -------------------
        # 格式错误、无效
        count_invalid = obj.error_count
        # 一共发送数
        send_total = count_send + count_invalid
        # -------------------

        # 邮箱不存在
        count_err_1 = value['count_err_1'] if value['count_err_1'] else 0
        # 空间不足
        count_err_2 = value['count_err_2'] if value['count_err_2'] else 0
        # 用户拒收
        count_err_3 = value['count_err_3'] if value['count_err_3'] else 0
        # 垃圾拒绝发送
        count_err_5 = value['count_err_5'] if value['count_err_5'] else 0
        total_error = count_invalid + count_err_1 + count_err_2 + count_err_3 + count_err_5

        # 邮件打开
        stat_objs = TrackStat.objects.filter(task_ident=obj.send_name, customer_id=request.user.id)
        stat_obj = stat_objs[0] if stat_objs else None
        open_unique, click_unique = 0, 0
        show_stat_rate, show_link_rate, show_link_rate_suc = '0%', '0%',  '0%'

        # 浏览器、操作系统、 地域 点击链接 统计
        link_objs = None
        ip_search = IpSearch()
        browser_count = {'ie': 0, 'firefox': 0, 'chrome': 0, 'other': 0}
        os_count = {'windows': 0, 'linux': 0, 'macintosh': 0, 'other': 0}
        area_list, area_lists, country_list, country_lists = [], {}, [], {}
        domain_data_click, domain_data_all = [], []
        track_id = 0
        pattern ='([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])'
        ip_compile = re.compile(pattern)
        if stat_objs:
            track_id = stat_obj.id
            # open_total = stat_obj.open_total
            open_unique = stat_obj.open_unique
            click_unique = stat_obj.click_unique
            show_stat_rate = statistics_tools.get_rate(stat_obj.open_unique, count_succes)
            show_link_rate = statistics_tools.get_rate(click_unique, open_unique)
            show_link_rate_suc = statistics_tools.get_rate(click_unique, count_succes)

            link_objs = TrackLink.objects.filter(track_id=track_id).order_by('-click_unique', '-click_total')[:50]
            cr = connections['mm-track'].cursor()
            tablename = '{}_track_email'.format(request.user.id)

            sql = u""" SELECT email FROM {0} WHERE track_id={1} AND click_total > 0; """.format(tablename, track_id)
            cr.execute(sql)
            domain_data_click = statistics_tools.get_domain_data(cr.fetchall())

            sql = u""" SELECT email FROM {0} WHERE track_id={1} AND open_total > 0; """.format(tablename, track_id)
            cr.execute(sql)
            domain_data_all = statistics_tools.get_domain_data(cr.fetchall())

            # 地域分布
            sql = u"""
            SELECT browser, os, ip_first, ip_last, open_total, click_total, email
            FROM {0} WHERE track_id={1};
            """.format(tablename, track_id)
            cr.execute(sql)
            rows = cr.fetchall()

            for row in rows:
                if row[0].lower().startswith('msie'):
                    browser_count['ie'] += 1
                elif row[0].lower().startswith('firefox'):
                    browser_count['firefox'] += 1
                elif row[0].lower().startswith('chrome'):
                    browser_count['chrome'] += 1
                else:
                    browser_count['other'] += 1

                if row[1].lower().startswith('windows'):
                    os_count['windows'] += 1
                elif row[1].lower().startswith('linux'):
                    os_count['linux'] += 1
                elif row[1].lower().startswith('macintosh'):
                    os_count['macintosh'] += 1
                else:
                    os_count['other'] += 1

                ip = ''
                if row[2]:
                    ip = row[2]
                elif row[3]:
                    ip = row[3]
                if not ip:
                    continue

                m = ip_compile.search(ip)
                if m:
                    ip = m.group(0)
                else:
                    continue

                ip_info = ip_search.Find(ip)
                country, area = statistics_tools.split_ip_info(ip_info)
                if not country:
                    continue
                if country not in country_list:
                    country_list.append(country)
                    country_lists.update({ country: [row[4], 1] })
                else:
                    country_lists.update({
                        country: [
                            country_lists[country][0] + row[4],
                            country_lists[country][1] + 1,
                            ]
                    })

                if not area:
                    continue

                if area not in area_list:
                    area_list.append(area)
                    area_lists.update({ area: [row[4], 1] })
                else:
                    area_lists.update({
                        area: [
                            area_lists[area][0] + row[4],
                            area_lists[area][1] + 1,
                            ]
                    })

        area_sort_tmp = sorted(area_lists.items(),key=lambda e:e[1][0], reverse=True)[:10]
        country_sort_tmp = sorted(country_lists.items(),key=lambda e:e[1][0], reverse=True)[:10]
        area_data, country_data = {}, {}
        area_sort, country_sort = [], []
        for d in area_sort_tmp:
            if d[0] in AREA_CODE.keys():
                area_data.update({
                    AREA_CODE[d[0]]: int(d[1][0]),
                })
            area_sort.append(
                (d[0], int(d[1][0]), int(d[1][1]))
            )
        for d in country_sort_tmp:
            if d[0] in JC_CODE_COUNTRY:
                country_data.update({
                    JC_CODE_COUNTRY[d[0]]: int(d[1][0]),
                })
            country_sort.append(
                (d[0], int(d[1][0]), int(d[1][1]))
            )
        area_max = statistics_tools.get_gfc_max_data(area_sort_tmp[0][1][0]) if area_sort_tmp else 5000
        country_max = statistics_tools.get_gfc_max_data(country_sort_tmp[0][1][0]) if area_sort_tmp else 5000

        context = {
            'task_obj': obj,
            'task_id': task_id,
            'task_send_total': task_send_total,
            'send_total': send_total,
            'count_send': count_send,
            'count_succes': count_succes,
            'count_succes_rate': statistics_tools.get_rate(count_succes, count_send - count_err_5),
            'count_error': count_error,
            'count_error_rate': statistics_tools.get_rate(count_error - count_err_5, count_send - count_err_5),

            'total_error': total_error,
            'count_invalid': {'value': count_invalid, 'width':  statistics_tools.get_width(count_invalid, total_error), 'rate': statistics_tools.get_rate(count_invalid, total_error)},
            'count_err_1': {'value': count_err_1, 'width':  statistics_tools.get_width(count_err_1, total_error), 'rate': statistics_tools.get_rate(count_err_1, total_error)},
            'count_err_2': {'value': count_err_2, 'width':  statistics_tools.get_width(count_err_2, total_error), 'rate': statistics_tools.get_rate(count_err_2, total_error)},
            'count_err_3': {'value': count_err_3, 'width':  statistics_tools.get_width(count_err_3, total_error), 'rate': statistics_tools.get_rate(count_err_3, total_error)},
            'count_err_5': {'value': count_err_5, 'width':  statistics_tools.get_width(count_err_5, total_error), 'rate': statistics_tools.get_rate(count_err_5, total_error)},

            'stat_obj': stat_obj,
            'show_stat_rate': show_stat_rate,
            'open_unique': open_unique,
            'open_unique_rate': statistics_tools.get_rate(open_unique, count_succes),
            'no_open': count_succes - open_unique,
            'no_open_rate': statistics_tools.get_rate(count_succes - open_unique, count_succes),

            'click_unique': click_unique,
            'show_link_rate': show_link_rate,
            'show_link_rate_suc': show_link_rate_suc,
            'no_click': count_succes - click_unique,
            'no_click_rate': statistics_tools.get_rate(count_succes - click_unique, count_succes),

            'link_objs': link_objs,
            'track_id':track_id,
            'domain_data_click': domain_data_click,
            'domain_data_all': domain_data_all,

            'area_sort': area_sort,
            'country_sort': country_sort,
            'area_data': area_data,
            'country_data': country_data,
            'area_max': area_max,
            'country_max':country_max,
            'os_count': os_count,
            'browser_count': browser_count,

            'filename': u"{}_{}.pdf".format(obj.send_name, task_id)
        }
        # cache.set(key, context, 300)
    return context
