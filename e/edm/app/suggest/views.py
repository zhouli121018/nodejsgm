# coding=utf-8
import re
import json
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from app.suggest.models import Suggest, SuggestDetail

@login_required
def ajax_suggest(request):
    msg = {'ret': "N"}
    url = request.GET.get('url', '').strip('')
    if url and url != '/':
        if re.search(r'(\/\d+?\/)', url):
            url = re.sub(r'(\/\d+?\/)', '/modify/', url)
        obj = Suggest.objects.filter(path=url).first()
        if obj: msg = {'ret': "Y"}
    return HttpResponse(
        json.dumps(msg, ensure_ascii=False ),
        content_type="application/json")

@login_required
def ajax_suggest_post(request):
    url = request.POST.get('url', '').strip('')
    suggest = request.POST.get('suggest', '').strip('')
    if suggest and url:
        if re.search(r'(\/\d+?\/)', url):
            url = re.sub(r'(\/\d+?\/)', '/modify/', url)
        obj = Suggest.objects.filter(path=url).first()
        if obj:
            SuggestDetail.objects.create(suggest=obj, customer=request.user, remark=suggest)
    return HttpResponse(
        json.dumps({"ret":"Y"}, ensure_ascii=False ),
        content_type="application/json")