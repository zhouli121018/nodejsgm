# coding=utf-8

import re
import time
import json
import base64
import phpserialize

from binascii import a2b_hex
from Crypto.Cipher import DES
from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django_user_agents.utils import get_user_agent
from django_redis import get_redis_connection
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db import connections
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from lib import ipparse
from lib.IpSearch import IpSearch
from lib.common import get_client_ip
from lib.excel_response import ExcelResponse

from app.track.utils import contexts
from app.track.models import TrackStat, TrackLink


def get_user_agent_info(request):
    user_agent = get_user_agent(request)
    return {
        'browser': '{} {}'.format(user_agent.browser.family, user_agent.browser.version_string),
        'os': '{} {}'.format(user_agent.os.family, user_agent.os.version_string),
        # 'ip': request.META['REMOTE_ADDR'],
        'ip': get_client_ip(request)
    }


# 任务点击打开统计
def track_statistic(request, track_params):
    is_gif = False
    if track_params.endswith('.gif'):
        is_gif = True
        track_params = track_params[:-4]
    try:
        obj = DES.new(settings.CRYP_KEY)
        params = obj.decrypt(a2b_hex(track_params))
    except:
        raise Http404
    if is_gif:
        task_ident, email = params.split('||')
        link = ''
    else:
        params = params.split('||')
        task_ident, email, link = params[:3]
        try:
            valid_key = params[3].strip()
        except:
            valid_key = ''
        if valid_key and valid_key != settings.CRYP_KEY:
            raise Http404

    redis = get_redis_connection()
    agent_info = get_user_agent_info(request)
    msg = phpserialize.dumps([time.time(), task_ident, email, link, agent_info])
    redis.rpush('track_stat_cache', msg)
    redis.rpush('active_emails_cache', msg)
    if is_gif:
        image_data = "R0lGODlhEAAQAOYAAAAAAP///zqKNj2NOT2MOUKSPj+OOkCPO0GQPEKRPUOSPkaWQUWUQEeWQkqZRU6dSE+eSU2cSFKhTFGgS1WkT2KsXGOtXXzDdlm1T1u2UVqpU1mnUma7XV6tV12rVmOxW2GvWmu9YmW0Xme1X2u5Y2q4Ymy1ZW21ZoHGeoPHfIHGe4TIfoXIfofKgIjKgYnKgorLg4nKg123Ul+4U2C5VWG6VmG5VmS7WGS7WWO6WGa7Wm+/ZXHAZm68ZW+9ZnLBaXLAaXbEbXfEbXvJcXjGb3rHcH3Lc33Kc3zJcoDOdn7LdIPQeYLPeILNeHrAcoXJfIjKgIvMg4zMhI3NhY7NhpDPiJLPipPPi2i8W2m9XWm8XWq9Xm2/YGy+X2/AYnHBZHLBZXPCZ4HOdoDNdZHPiJTPipfSjZTPi5XPi5bRjZXQjJnSkJjRj5zUk57VlXPCZXfDaYfLeZ3Vk6LYl6HXlqHXl6LYmKLXmKPYmaTYmabZm6fZnP///wAAAAAAAAAAACH5BAEAAHwALAAAAAAQABAAAAeogHyCg4SFhkxjR0WGhk17dkGMhUhzZkCSS2JKQ0R1cj0lIx+FSXp5d3RubWxqZR2FRnh1cXBvX2E8ZxqFRUJPbWBeXVk6VScSDw6EPmtcW1g4NTtRL1ALhCRpWjo5NDIhLiwrBYKgTlc3NTMZGC0VDAkGgiVoVj9UUjAuHCsMhSJkbEwxIQGChRQqEBQCgS+GBEENUFwYUMjDBgoTIghScICAAEkgBwUCADs=";
        return HttpResponse(base64.b64decode(image_data), content_type='image/gif')
    else:
        response = HttpResponse("", status=302)
        link = link.replace('&amp;', '&')
        response['Location'] = link
        return response

# 任务点击打开统计
def track_statistic2(request, track_params):
    is_gif = False
    if track_params.endswith('.gif'):
        is_gif = True
        track_params = track_params[:-4]
    try:
        obj = DES.new(settings.CRYP_KEY)
        params = obj.decrypt(a2b_hex(track_params))
    except:
        raise Http404
    if is_gif:
        task_ident, email = params.split('||')
        link = ''
    else:
        try:
            params = params.split('||')
            task_ident, email, link, valid_key = params[:4]
            assert valid_key.strip() == settings.CRYP_KEY
        except:
            raise Http404

    redis = get_redis_connection()
    agent_info = get_user_agent_info(request)
    msg = phpserialize.dumps([time.time(), task_ident, email, link, agent_info])
    redis.rpush('track_stat_cache', msg)
    redis.rpush('active_emails_cache', msg)
    if is_gif:
        image_data = "R0lGODlhEAAQAOYAAAAAAP///zqKNj2NOT2MOUKSPj+OOkCPO0GQPEKRPUOSPkaWQUWUQEeWQkqZRU6dSE+eSU2cSFKhTFGgS1WkT2KsXGOtXXzDdlm1T1u2UVqpU1mnUma7XV6tV12rVmOxW2GvWmu9YmW0Xme1X2u5Y2q4Ymy1ZW21ZoHGeoPHfIHGe4TIfoXIfofKgIjKgYnKgorLg4nKg123Ul+4U2C5VWG6VmG5VmS7WGS7WWO6WGa7Wm+/ZXHAZm68ZW+9ZnLBaXLAaXbEbXfEbXvJcXjGb3rHcH3Lc33Kc3zJcoDOdn7LdIPQeYLPeILNeHrAcoXJfIjKgIvMg4zMhI3NhY7NhpDPiJLPipPPi2i8W2m9XWm8XWq9Xm2/YGy+X2/AYnHBZHLBZXPCZ4HOdoDNdZHPiJTPipfSjZTPi5XPi5bRjZXQjJnSkJjRj5zUk57VlXPCZXfDaYfLeZ3Vk6LYl6HXlqHXl6LYmKLXmKPYmaTYmabZm6fZnP///wAAAAAAAAAAACH5BAEAAHwALAAAAAAQABAAAAeogHyCg4SFhkxjR0WGhk17dkGMhUhzZkCSS2JKQ0R1cj0lIx+FSXp5d3RubWxqZR2FRnh1cXBvX2E8ZxqFRUJPbWBeXVk6VScSDw6EPmtcW1g4NTtRL1ALhCRpWjo5NDIhLiwrBYKgTlc3NTMZGC0VDAkGgiVoVj9UUjAuHCsMhSJkbEwxIQGChRQqEBQCgS+GBEENUFwYUMjDBgoTIghScICAAEkgBwUCADs=";
        return HttpResponse(base64.b64decode(image_data), content_type='image/gif')
    else:
        response = HttpResponse("", status=302)
        link = link.replace('&amp;', '&')
        response['Location'] = link
        return response


# 任务点击打开统计
def track_statistic3(request, track_params):
    is_gif = False
    if track_params.endswith('.gif'):
        is_gif = True
        track_params = track_params[:-4]
    elif track_params.endswith('.html'):
        track_params = track_params[:-5]

    try:
        params = base64.urlsafe_b64decode(track_params.encode('utf-8'))
    except:
        raise Http404
    params_list = params.split('||')

    if is_gif:
        link = ''
        if len(params_list) == 2:
            content_id = ''
            task_ident, email = params_list[:2]
        else:
            task_ident, email, content_id = params_list[:3]
    else:
        if len(params_list) == 3:
            content_id = ''
            task_ident, email, link = params.split('||')[:3]
        else:
            task_ident, email, link, content_id = params.split('||')[:4]

    redis = get_redis_connection()
    agent_info = get_user_agent_info(request)
    http_referer = request.META.get('HTTP_REFERER', '')
    if agent_info['ip'] not in ["171.13.131.85", "218.77.130.133", "60.28.2.248", '60.28.175.38'] and not agent_info['ip'].startswith(
            '121.42.0.') and http_referer.find('admin.mailrelay.cn') == -1:
        result = json.dumps([time.time(), task_ident, email, link, agent_info, content_id])
        (redis.pipeline()
         .rpush(':umailtrack:track:stat:', result)
         .rpush(':umailtrack:track:active:', result)
         .rpush('trigger_waiting', result)
         .execute())

        # msg = phpserialize.dumps(result)
        # redis.rpush('track_stat_cache', msg)
        # redis.rpush('active_emails_cache', msg)
    if is_gif:
        image_data = "R0lGODlhEAAQAOYAAAAAAP///zqKNj2NOT2MOUKSPj+OOkCPO0GQPEKRPUOSPkaWQUWUQEeWQkqZRU6dSE+eSU2cSFKhTFGgS1WkT2KsXGOtXXzDdlm1T1u2UVqpU1mnUma7XV6tV12rVmOxW2GvWmu9YmW0Xme1X2u5Y2q4Ymy1ZW21ZoHGeoPHfIHGe4TIfoXIfofKgIjKgYnKgorLg4nKg123Ul+4U2C5VWG6VmG5VmS7WGS7WWO6WGa7Wm+/ZXHAZm68ZW+9ZnLBaXLAaXbEbXfEbXvJcXjGb3rHcH3Lc33Kc3zJcoDOdn7LdIPQeYLPeILNeHrAcoXJfIjKgIvMg4zMhI3NhY7NhpDPiJLPipPPi2i8W2m9XWm8XWq9Xm2/YGy+X2/AYnHBZHLBZXPCZ4HOdoDNdZHPiJTPipfSjZTPi5XPi5bRjZXQjJnSkJjRj5zUk57VlXPCZXfDaYfLeZ3Vk6LYl6HXlqHXl6LYmKLXmKPYmaTYmabZm6fZnP///wAAAAAAAAAAACH5BAEAAHwALAAAAAAQABAAAAeogHyCg4SFhkxjR0WGhk17dkGMhUhzZkCSS2JKQ0R1cj0lIx+FSXp5d3RubWxqZR2FRnh1cXBvX2E8ZxqFRUJPbWBeXVk6VScSDw6EPmtcW1g4NTtRL1ALhCRpWjo5NDIhLiwrBYKgTlc3NTMZGC0VDAkGgiVoVj9UUjAuHCsMhSJkbEwxIQGChRQqEBQCgS+GBEENUFwYUMjDBgoTIghScICAAEkgBwUCADs=";
        return HttpResponse(base64.b64decode(image_data), content_type='image/gif')
    else:
        response = HttpResponse("", status=302)
        link = link.replace('&amp;', '&')
        response['Location'] = link
        return response


# 任务点击打开统计
def track_statistic4(request, track_params):
    is_gif = False
    if track_params.endswith('.gif'):
        is_gif = True
        track_params = track_params[:-4]
    elif track_params.endswith('.html'):
        track_params = track_params[:-5]

    try:
        params = base64.urlsafe_b64decode(track_params.encode('utf-8'))
    except:
        raise Http404
    params_list = params.split('||')

    if is_gif:
        link = ''
        if len(params_list) == 2:
            content_id = ''
            task_ident, email = params_list[:2]
        else:
            content_id, task_ident, email = params_list[:3]
    else:
        if len(params_list) == 3:
            content_id = ''
            task_ident, email, link = params.split('||')[:3]
        else:
            content_id, task_ident, email, link = params.split('||')[:4]

    redis = get_redis_connection()
    agent_info = get_user_agent_info(request)
    http_referer = request.META.get('HTTP_REFERER', '')
    if agent_info['ip'] not in ["171.13.131.85", "218.77.130.133", "60.28.2.248", "58.63.235.22", "60.28.175.38"] and not agent_info['ip'].startswith(
            '121.42.0.') and http_referer.find('admin.mailrelay.cn') == -1:
        result = json.dumps([time.time(), task_ident, email, link, agent_info, content_id])
        (redis.pipeline()
         .rpush(':umailtrack:track:stat:', result)
         .rpush(':umailtrack:track:active:', result)
         .rpush('trigger_waiting', result)
         .execute())

        # msg = phpserialize.dumps(result)
        # redis.rpush('track_stat_cache', msg)
        # redis.rpush('active_emails_cache', msg)
    if is_gif:
        image_data = "R0lGODlhEAAQAOYAAAAAAP///zqKNj2NOT2MOUKSPj+OOkCPO0GQPEKRPUOSPkaWQUWUQEeWQkqZRU6dSE+eSU2cSFKhTFGgS1WkT2KsXGOtXXzDdlm1T1u2UVqpU1mnUma7XV6tV12rVmOxW2GvWmu9YmW0Xme1X2u5Y2q4Ymy1ZW21ZoHGeoPHfIHGe4TIfoXIfofKgIjKgYnKgorLg4nKg123Ul+4U2C5VWG6VmG5VmS7WGS7WWO6WGa7Wm+/ZXHAZm68ZW+9ZnLBaXLAaXbEbXfEbXvJcXjGb3rHcH3Lc33Kc3zJcoDOdn7LdIPQeYLPeILNeHrAcoXJfIjKgIvMg4zMhI3NhY7NhpDPiJLPipPPi2i8W2m9XWm8XWq9Xm2/YGy+X2/AYnHBZHLBZXPCZ4HOdoDNdZHPiJTPipfSjZTPi5XPi5bRjZXQjJnSkJjRj5zUk57VlXPCZXfDaYfLeZ3Vk6LYl6HXlqHXl6LYmKLXmKPYmaTYmabZm6fZnP///wAAAAAAAAAAACH5BAEAAHwALAAAAAAQABAAAAeogHyCg4SFhkxjR0WGhk17dkGMhUhzZkCSS2JKQ0R1cj0lIx+FSXp5d3RubWxqZR2FRnh1cXBvX2E8ZxqFRUJPbWBeXVk6VScSDw6EPmtcW1g4NTtRL1ALhCRpWjo5NDIhLiwrBYKgTlc3NTMZGC0VDAkGgiVoVj9UUjAuHCsMhSJkbEwxIQGChRQqEBQCgS+GBEENUFwYUMjDBgoTIghScICAAEkgBwUCADs=";
        return HttpResponse(base64.b64decode(image_data), content_type='image/gif')
    else:
        response = HttpResponse("", status=302)
        link = link.replace('&amp;', '&').replace('\n', '')
        response['Location'] = link
        return response

@login_required
def track_task_stat(request):
    """ 根据跟踪任务获取，这个更准确 """
    try:
        context = contexts.get_track_context(request)
        return render(request, 'track/track_task.html', context=context)
    except Exception as e:
        # import sys
        # import traceback
        # print >> sys.stderr, e
        # print >> sys.stderr, traceback.format_exc()
        return HttpResponse(_(u'此任务暂无跟踪统计数据！'))


@login_required
def ajax_track_task_link(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    content_id = data.get('content_id', '')

    ident = data.get('ident', '')
    user_id = request.user.id
    stat_objs = TrackStat.objects.filter(task_ident=ident, customer_id=user_id)
    if content_id:
        stat_objs = stat_objs.filter(content_id=content_id)

    lists = TrackLink.objects.filter(track__in=stat_objs)

    colums = ['id', 'link', 'click_unique', 'click_total', 'click_first', 'click_last']
    if search:
        lists = lists.filter(link__icontains=search)

    if lists.exists() and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = lists.order_by('-%s' % colums[int(order_column)])
        else:
            lists = lists.order_by('%s' % colums[int(order_column)])
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        start_num = int(data.get('start', '0'))
        page = start_num / length + 1
    except ValueError:
        start_num = 0
        page = 1
    count = lists.count()
    if start_num >= count:
        page = 1

    paginator = Paginator(lists, length)

    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page - 1) + 1
    for obj in lists.object_list:
        t = TemplateResponse(request, 'track/ajax_track_task_link.html', {'obj': obj, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

# 查看邮件地址统计
@login_required
def track_email(request, track_id):
    customer_id = request.user.id
    obj = TrackStat.objects.get(id=track_id, customer_id=customer_id)
    ident = obj.task_ident
    open_total = obj.open_total
    open_unique = obj.open_unique
    return render(request, 'track/track_email.html', context={
        'ident': ident,
        'track_id': track_id,
        'open_total': open_total,
        'open_unique': open_unique,
    })


# 查看邮件地址统计
@login_required
def track_open_info(request):
    customer_id = request.user.id
    ident = request.GET.get('ident', '')
    content_id = request.GET.get('content_id', '')
    stat_objs = TrackStat.objects.filter(task_ident=ident, customer_id=customer_id)
    if content_id:
        stat_objs = stat_objs.filter(content_id=content_id)

    track_stat = stat_objs.aggregate(open_total=Sum('open_total'), open_unique=Sum('open_unique'))
    open_total = track_stat['open_total']
    open_unique = track_stat['open_unique']
    return render(request, 'track/track_open_info.html', context={
        'ident': ident,
        'content_id': content_id,
        'open_total': open_total,
        'open_unique': open_unique,
        'stat_objs': stat_objs
    })

@login_required
def ajax_track_email(request):
    data = request.GET
    user_id = request.user.id
    cr = connections['mm-track'].cursor()
    tablename = '{}_track_email'.format(user_id)
    ident = data.get('ident', '')
    content_id = data.get('content_id', '')
    stat_objs = TrackStat.objects.filter(task_ident=ident, customer_id=user_id)
    if content_id:
        stat_objs = stat_objs.filter(content_id=content_id)
    track_ids = stat_objs.values_list('id', flat=True)
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['email_id', 'email', 'open_total', 'browser', 'ip_first', 'open_first', 'click_first']

    where_str = u'track_id in ({})'.format(','.join(map(lambda s: str(s), track_ids)))
    if search:
        where_str += u""" and email like '%{0}%' """.format(search)

    order_by_str = ''
    if order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            order_by_str = u'order by %s desc' % colums[int(order_column)]
        else:
            order_by_str = u'order by %s asc' % colums[int(order_column)]

    sql = u"SELECT COUNT(1) FROM %s WHERE %s;" % (tablename, where_str)
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
    limit_str = u'limit %s offset %s' % (length, start_num)
    sql = u"""
    SELECT email, open_total, click_total, browser, os, ip_first, ip_last,
            open_first, open_last, click_first, click_last, email_id
    FROM %s WHERE %s %s %s;
    """ % (tablename, where_str, order_by_str, limit_str)
    cr.execute(sql)
    rows = cr.fetchall()
    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    page = start_num / length + 1
    number = length * (page - 1) + 1
    ip_search = IpSearch()
    # pattern ='([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])'
    pattern = '(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)'
    ip_compile = re.compile(pattern)
    lang_code = ( request.user.lang_code == 'en-us' and 'en-us') or "zh-hans"
    for r in rows:
        email, open_total, click_total, browser, os, ip_first, ip_last, open_first, open_last, click_first, click_last, email_id = r
        open_first = open_first if open_first else u'-'
        open_last = open_last if open_last else u'-'
        click_first = click_first if click_first else u'-'
        click_last = click_last if click_last else u'-'
        ip_first_html = _(u'首：<span style="cursor: default;color: #004F99;font-size: 11px;">-</span>') % {}
        ip_last_html = _(u'<br>后：<span style="cursor: default;color: #CC0000;font-size: 11px;">-</span>') % {}
        if ip_first:
            m = ip_compile.search(ip_first)
            if m:
                ip_first = m.group(0)
                ip_info = ip_search.Find(ip_first)
                area, title = ipparse.get_ip_detail(ip_info, lang_code)
                ip_first_html = _(
                    u'首：<span style="color: Gray;" title="%(title)s">[%(area)s] </span><span style="cursor: default;color: #004F99;font-size: 11px;">%(ip_first)s</span>') % {
                                    'title': title, 'area': area, 'ip_first': ip_first}
        if ip_last:
            m = ip_compile.search(ip_last)
            if m:
                ip_last = m.group(0)
                ip_info = ip_search.Find(ip_last)
                area, title = ipparse.get_ip_detail(ip_info, lang_code)
                ip_last_html = _(
                    u'<br>后：<span style="color: Gray;" title="%(title)s">[%(area)s] </span><span style="cursor: default;color: #004F99;font-size: 11px;">%(ip_last)s</span>') % {
                                   'title': title, 'area': area, 'ip_last': ip_last}
        ip_html = ip_first_html + ip_last_html
        rs["aaData"].append([
            number, email,
            _(
                u""" %(open_total)d / <a href='/track/click/?ident=%(ident)s&content_id=%(content_id)s&email_id=%(email_id)d' title='查看点击详情'>%(click_total)d</a>""") % {
                'open_total': int(open_total), 'ident': ident, 'content_id': content_id, 'email_id': int(email_id),
                'click_total': int(click_total)},
            u'{}<br>{}'.format(browser, os),
            ip_html,
            _(
                u'首：<span style="cursor: default;color: #004F99;font-size: 11px;">%(open_first)s</span><br>后：<span style="cursor: default;color: #CC0000;font-size: 11px;">%(open_last)s</span>') % {
                'open_first': open_first, 'open_last': open_last},
            _(
                u'首：<span style="cursor: default;color: #004F99;font-size: 11px;">%(click_first)s</span><br>后：<span style="cursor: default;color: #CC0000;font-size: 11px;">%(click_last)s</span>') % {
                'click_first': click_first, 'click_last': click_last},
            "",
        ])
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


# 查看链接统计
@login_required
def track_click(request, track_id):
    customer_id = request.user.id
    if not track_id:
        track_id = request.GET.get('track_id')
    obj = TrackStat.objects.get(id=track_id, customer_id=customer_id)
    ident = obj.task_ident
    click_total = obj.click_total
    click_unique = obj.click_unique
    return render(request, 'track/track_click.html', context={
        'ident': ident,
        'track_id': track_id,
        'click_total': click_total,
        'click_unique': click_unique,
    })


# 查看链接统计
@login_required
def track_click_info(request):
    customer_id = request.user.id
    ident = request.GET.get('ident', '')
    content_id = request.GET.get('content_id', '')
    stat_objs = TrackStat.objects.filter(task_ident=ident, customer_id=customer_id)
    if content_id:
        stat_objs = stat_objs.filter(content_id=content_id)

    track_stat = stat_objs.aggregate(click_total=Sum('click_total'), click_unique=Sum('click_unique'))
    click_total = track_stat['click_total']
    click_unique = track_stat['click_unique']
    return render(request, 'track/track_click_info.html', context={
        'ident': ident,
        'content_id': content_id,
        'open_total': click_total,
        'open_unique': click_unique,
        'stat_objs': stat_objs
    })


@login_required
def ajax_track_click(request):
    data = request.GET
    user_id = request.user.id
    cr = connections['mm-track'].cursor()
    tablename = '{}_track_click'.format(user_id)
    tablename_email = '{}_track_email'.format(user_id)
    ident = data.get('ident', '')
    content_id = data.get('content_id', '')
    track_id = data.get('track_id', '')
    stat_objs = TrackStat.objects.filter(task_ident=ident, customer_id=user_id)
    if content_id:
        stat_objs = stat_objs.filter(content_id=content_id)
    track_ids = stat_objs.values_list('id', flat=True)
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    link_id = data.get('link_id', '')
    email_id = data.get('email_id', '')
    colums = ['click_id', 'email_id', 'link_id', 'click_unique', 'click_total', 'click_first', 'click_last']

    if ident:
        where_str = u'track_id in ({})'.format(','.join(map(lambda s: str(s), track_ids)))
    elif track_id:
        where_str = u'track_id = {}'.format(track_id)
    search_flag = True
    if search:
        cr.execute("SELECT email_id FROM {0} WHERE email LIKE '%{1}%';".format(tablename_email, search))
        email_ids = cr.fetchall()
        if email_ids:
            email_ids = [int(r[0]) for r in email_ids]
            where_str += u""" and email_id in ({}) """.format(','.join(map(str, email_ids)))
        else:
            search_flag = False
    if link_id:
        where_str += u""" and link_id={} """.format(link_id)
    if email_id:
        where_str += u""" and email_id={} """.format(email_id)

    order_by_str = ''
    if order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            order_by_str = u'order by %s desc' % colums[int(order_column)]
        else:
            order_by_str = u'order by %s asc' % colums[int(order_column)]

    sql = u"SELECT COUNT(1) FROM %s WHERE %s;" % (tablename, where_str)
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
    if search_flag:
        limit_str = u'limit %s offset %s' % (length, start_num)
        sql = u"""
        SELECT click_id, email_id, link_id, click_unique, click_total, click_first, click_last
        FROM %s WHERE %s %s %s;
        """ % (tablename, where_str, order_by_str, limit_str)
        cr.execute(sql)
        rows = cr.fetchall()
    else:
        rows = []
    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    page = start_num / length + 1
    number = length * (page - 1) + 1
    for r in rows:
        click_id, email_id, link_id, click_unique, click_total, click_first, click_last = r
        if not cr.execute("SELECT email FROM {} WHERE email_id={};".format(tablename_email, email_id)):
            continue
        email = cr.fetchone()[0]
        link_obj = TrackLink.objects.get(id=link_id, customer_id=user_id)
        link = link_obj.link
        click_unique = click_unique if click_unique else 0
        click_total = click_total if click_total else 0
        click_first = click_first if click_first else u'-'
        click_last = click_last if click_last else u'-'
        rs["aaData"].append([
            number, email, link, click_unique, click_total,
            u'<span style="cursor: default;color: #004F99;font-size: 11px;">{}</span>'.format(click_first),
            u'<span style="cursor: default;color: #CC0000;font-size: 11px;">{}</span>'.format(click_last),
            "",
        ])
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


# 导出地址
@login_required
def track_export_email(request):
    if not request.user.service().is_track_export:
        raise Http404
    data = request.GET
    action = data.get('action', '')
    link_id = data.get('link_id', '')
    user_id = request.user.id

    ident = data.get('ident', '')
    content_id = data.get('content_id', '')
    stat_objs = TrackStat.objects.filter(task_ident=ident, customer_id=user_id)
    if content_id:
        stat_objs = stat_objs.filter(content_id=content_id)
    track_ids = stat_objs.values_list('id', flat=True)

    cr = connections['mm-track'].cursor()
    tablename = '{}_track_email'.format(user_id)
    tablename_click = '{}_track_click'.format(user_id)
    if request.user.lang_code == 'en-us':
        list = [
            [u'邮件地址', u'首次使用IP', u'首次IP区域', u'最后使用IP', u'最后IP区域', u'打开总数',
             u'首次打开时间', u'最后打开时间', u'点击总数', u'首次点击时间', u'最后点击时间']
        ]
    else:
        list = [
            [u'邮件地址', u'首次使用IP', u'首次IP区域', u'最后使用IP', u'最后IP区域', u'打开总数',
             u'首次打开时间', u'最后打开时间', u'点击总数', u'首次点击时间', u'最后点击时间']
        ]
    sql = """
    SELECT email, ip_first, COALESCE(ip_last, '') ip_last,
            open_total, open_first, COALESCE(open_last, '') open_last,
            click_total, COALESCE(click_first, '') click_first, COALESCE(click_last, '') click_last
    FROM {} WHERE track_id in ({})""".format(tablename, ','.join(map(lambda s: str(s), track_ids)))
    where_str = ''
    if action == 'click':
        where_str += " AND click_total > 0 "
    if link_id:
        where_str += " AND email_id IN (SELECT email_id FROM {} WHERE link_id={})".format(tablename_click, link_id)
    sql += where_str
    cr.execute(sql)
    rows = cr.fetchall()
    ip_search = IpSearch()
    # pattern ='([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])'
    pattern = '(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)'
    ip_compile = re.compile(pattern)
    lang_code = ( request.user.lang_code == 'en-us' and 'en-us') or "zh-hans"
    for r in rows:
        title_f, title_l = '', ''
        email, ip_first, ip_last, open_total, open_first, open_last, click_total, click_first, click_last = r
        open_last = '' if open_last == '0000-00-00 00:00:00' else open_last
        click_first = '' if click_first == '0000-00-00 00:00:00' else click_first
        click_last = '' if click_last == '0000-00-00 00:00:00' else click_last
        if ip_first:
            m = ip_compile.search(ip_first)
            if m:
                ip_first = m.group(0)
                ip_info = ip_search.Find(ip_first)
                area, title_f = ipparse.get_ip_detail(ip_info, lang_code)
        if ip_last:
            m = ip_compile.search(ip_last)
            if m:
                ip_last = m.group(0)
                ip_info = ip_search.Find(ip_last)
                area, title_l = ipparse.get_ip_detail(ip_info, lang_code)
        list.append(
            [email, ip_first, title_f, ip_last, title_l, open_total, open_first, open_last, click_total, click_first,
             click_last])
    return ExcelResponse(list, 'mail', encoding='gbk')
