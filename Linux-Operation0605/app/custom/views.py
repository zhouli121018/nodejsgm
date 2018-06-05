# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ConfigParser
import re
import json
import os

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from lib.tools import get_process_pid, restart_process, get_fail2ban_info, fail2ban_ip

from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.transaction import atomic
from django.db.models import Q
from django_redis import get_redis_connection

from app.core.models import DomainAttr, Domain
from app.custom.forms import CustomKKserverForm
from app.custom.models import CustomKKServerToken

from lib import validators
from lib.tools import fail2ban_ip, get_redis_connection
from lib.licence import licence_required


@licence_required
def custom_kkserver_settings(request):
    instance = DomainAttr.objects.filter(domain_id=0,type='system',item='sw_custom_kkserver_setting').first()
    form = CustomKKserverForm(instance=instance)
    if request.method == "POST":
        form = CustomKKserverForm(instance=instance, post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改设置成功')
    return render(request, "custom/kkserver_settings.html", context={
        "form": form,
    })
