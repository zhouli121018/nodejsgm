# -*- coding: utf-8 -*-

import os
import json
from math import ceil
from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django_redis import get_redis_connection
from django.utils import timezone
from app.address.forms import CaptchaTestForm
from captcha.models import CaptchaStore

# key

def invalidView(request, log_id):
    form = CaptchaTestForm()

    page = request.GET.get('page', '')
    # 每页展示数量
    page_count = 10
    # 页码
    try:
        page = page and int(page) or 1
    except:
        page = 1

    if request.method == "POST":
        data = request.POST
        res = False
        if CaptchaStore.objects.filter(response=data.get('captcha_1', '').lower(), hashkey=data.get('captcha_0', ''), expiration__gt=timezone.now()):
            res = True

        return HttpResponse(json.dumps({'res': res}, ensure_ascii=False), content_type="application/json")

    redis = get_redis_connection()
    invalid_key = "edm-web-invalid-view-{}-{}".format(request.user.id, log_id)

    try:
        k = int(redis.get(invalid_key))
    except:
        k = 0
        p = redis.pipeline()
        p.set(invalid_key, k)
        p.expire(invalid_key, 60*60)
        p.execute()
    need_verify = False
    max_try = 5
    if k >= max_try:
        need_verify = True
    if k > max_try:
        form = CaptchaTestForm(request.GET)
        if not form.is_valid():
            page = 1
            need_verify = True
    p = redis.pipeline()
    p.set(invalid_key, k+1)
    p.expire(invalid_key, 60*60)
    p.execute()

    invalid_lines_key = "edm-web-invalid-view-{}-{}-lines".format(request.user.id, log_id)
    lines = redis.get(invalid_lines_key)
    # if lines is None:
    if True:
        fname = '{}_maillist_err_t{}.txt'.format(log_id, 1)
        fpath = os.path.join("/usr/local/mail-import/data/", fname)
        lines = []
        if os.path.exists(fpath):
            with open(fpath, 'r') as f:
                lines = f.readlines()
            p = redis.pipeline()
            p.set(invalid_lines_key, json.dumps(lines))
            p.expire(invalid_lines_key, 15*60)
            p.execute()
    else:
        try:
            lines = json.loads(lines)
        except:
            lines = []

    total_count = len(lines)
    total_page = int(ceil(float(total_count)/float(page_count)))
    if page<=0:
        page = 1
    if page>=total_page:
        page = total_page

    ctx = invalidPaginate(page, total_page, page_count, total_count, lines)
    return render(request, 'address/invalid_view.html', context={
        "log_id": log_id,
        "invalid_ctx": ctx,
        'captch_form': form,
        'need_verify': need_verify
    })

def invalidPaginate(page, total_page, page_count, total_count, lines):
    has_next = False
    if page<total_page:
        has_next = True
    has_previous = False
    if page>1:
        has_previous = True

    pages = getPages(page, total_page)

    # 获取 起始截止下标 都+1了
    start_num = (page-1) * page_count + 1
    if start_num > total_count:
        start_num=1
    end_num = start_num + page_count
    if end_num>total_count:
        end_num=total_count +1
        page_count = end_num-start_num
    else:
        end_num -= 1
    return {
        'need_veryfy': False,
        'lists': lines[start_num-1:end_num],
        'current_page': page,
        'pages': pages,
        'total_count': total_count,
        'has_previous': has_previous,
        'previous_page_number': page-1,
        'has_next': has_next,
        'next_page_number': page+1,

        'page_count': page_count,
        'start_num': start_num,
        'end_num': end_num-1,
    }

def getPages(page, total_page):
    pages = []
    if total_page<=5:
        pages.extend([i for i in range(1, total_page+1)])
    elif page>=5 and page>3 and total_page-page>3:
        pages.append(1)
        pages.append(None)
        pages.extend([i for i in range(page-2, page+3)])
        pages.append(None)
        pages.append(total_page)
    elif page<=5:
        pages = [i for i in range(1, 6)]
        pages.append(None)
        pages.append(total_page)
    else:
        pages.append(1)
        pages.append(None)
        pages.extend([i for i in range(total_page-5, total_page+1)])
    return pages
