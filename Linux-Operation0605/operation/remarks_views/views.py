# -*- coding: utf-8 -*-

import re
import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _lazy

from app.core.models import CoreUrlRemark


def ajax_get_remark(request):
    data = request.GET
    # print "data is  ",data
    base_url = data.get('base_url', '').strip('')
    lists = []
    if base_url:
        if re.search(r'(\/\d+?\/)', base_url):
            base_url = re.sub(r'(\/\d+?\/)', '/modify/', base_url)
        lists = CoreUrlRemark.objects.filter(url=base_url).values('remark')
    res = lists and lists[0] or {'remark': u''}
    callback = data.get("callback","")
    response = HttpResponse("%s(%s)"%(callback, json.dumps(res, ensure_ascii=False)), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"

    # print ">>>>>>>>>>>>>  response is ",response
    return response


def ajax_set_remark(request):
    data = request.GET
    # print "data is  ",data

    base_url = data.get('base_url', '').strip('')
    remark = data.get('remark', '').strip('')
    if base_url:
        if re.search(r'(\/\d+?\/)', base_url):
            base_url = re.sub(r'(\/\d+?\/)', '/modify/', base_url)
        obj, bool = CoreUrlRemark.objects.get_or_create(url=base_url)
        obj.remark = remark
        obj.save()

    callback = data.get("callback","")
    response = HttpResponse("%s(%s)"%(callback,json.dumps({'msg': _lazy(u"成功修改备注")%{}})), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"

    # print ">>>>>>>>>>>>>  response is ",response
    return response
