# -*- coding: utf-8 -*-
#
import json
from django import forms
from lib.forms import BaseFied, DotDict
from app.core.models import Mailbox, Domain, CoreAlias, DomainAttr

from lib import validators
from lib.formats import dict_compatibility
from lib.tools import clear_redis_cache

from django.utils.translation import ugettext_lazy as _
from app.maillog import constants
from app.core.models import DomainAttr, Mailbox, Department
from app.core.constants import MAILBOX_SEND_PERMIT,MAILBOX_RECV_PERMIT

import time
import copy

def get_department_list():
    l = [(u"0",u"所有部门")]
    for obj in Department.objects.all():
        l.append( (obj.id,obj.title) )
    return tuple(l)

class MailLogSearchForm(forms.Form):

    type = forms.ChoiceField(label=u'发送类型', choices=constants.MAILLOG_TYPE, required=False, initial="in")
    start_time = forms.DateTimeField(label=u'开始时间', required=False, widget=forms.DateTimeInput(attrs={'size':12}))
    end_time = forms.DateTimeField(label=u'结束时间', required=False, widget=forms.DateTimeInput(attrs={'size':12}))
    max_attach = forms.FloatField(label=u'最大附件', required=False, widget=forms.NumberInput(attrs={"id":"id_max_attach",'size':12, 'placeholder': u""}))
    min_attach = forms.FloatField(label=u'最小附件', required=False, widget=forms.NumberInput(attrs={"id":"id_min_attach",'size':12, 'placeholder': u""}))

    send_mail = forms.CharField(label=u'发信人', max_length=100, required=False, widget=forms.TextInput(attrs={"id":"id_send_mail",'size':12, 'placeholder': u""}))
    recv_mail = forms.CharField(label=u'收信人', max_length=100, required=False, widget=forms.TextInput(attrs={"id":"id_recv_mail",'size':12, 'placeholder': u""}))
    senderip = forms.CharField(label=u'发信服务器', max_length=100, required=False, widget=forms.TextInput(attrs={'size':12, 'placeholder': u""}))
    rcv_server = forms.CharField(label=u'收件服务器', max_length=100, required=False, widget=forms.TextInput(attrs={'size':12, 'placeholder': u""}))
    username = forms.CharField(label=u'用户名', max_length=100, required=False, widget=forms.TextInput(attrs={"id":"id_username",'size':12, 'placeholder': u""}))
    text = forms.CharField(label=u'标题/发件邮箱/收件邮箱/附件名称', max_length=200, required=False, widget=forms.TextInput(attrs={'size':12, 'placeholder': u""}))

    @property
    def get_start_time(self):
        return self.data.get("start_time","")

    @property
    def get_end_time(self):
        return self.data.get("end_time","")

    @property
    def get_senderip(self):
        return self.data.get("senderip","")

    @property
    def get_rcv_server(self):
        return self.data.get("rcv_server","")

    @property
    def get_text(self):
        return self.data.get("text","")

class MailboxStatForm(forms.Form):

    username = forms.CharField(label=u'用户名', max_length=100, required=False, widget=forms.TextInput(attrs={"id":"id_username",'size':12, 'placeholder': u""}))
    name = forms.CharField(label=u'用户姓名', max_length=100, required=False, widget=forms.TextInput(attrs={"id":"id_name",'size':12, 'placeholder': u""}))
    quota = forms.CharField(label=u'邮箱容量', max_length=100, required=False, widget=forms.NumberInput(attrs={"id":"id_quota",'size':12, 'placeholder': u""}))
    netdisk_quota = forms.CharField(label=u'网络硬盘容量', max_length=100, required=False, widget=forms.NumberInput(attrs={"id":"id_netdisk",'size':12, 'placeholder': u""}))

    send_permit = forms.ChoiceField(label=u'发送权限', required=False, choices=MAILBOX_SEND_PERMIT, widget=forms.Select(attrs={"id":"id_send_permit",'size':1}))
    recv_permit = forms.ChoiceField(label=u'接收权限', required=False, choices=MAILBOX_RECV_PERMIT, widget=forms.Select(attrs={"id":"id_recv_permit",'size':1}))

    department = forms.CharField(label=u'部门', max_length=100, required=False, widget=forms.TextInput(attrs={"id":"id_department",'size':12, 'placeholder': u""}))
    position = forms.CharField(label=u'职位', max_length=100, required=False, widget=forms.TextInput(attrs={"id":"id_position",'size':12, 'placeholder': u""}))
    worknumber = forms.CharField(label=u'工号', max_length=100, required=False, widget=forms.TextInput(attrs={"id":"id_worknumber",'size':12, 'placeholder': u""}))

class ActiveUserStatForm(forms.Form):

    dept_list = get_department_list()
    department = forms.ChoiceField(label=u'部门', required=False, choices=dept_list, widget=forms.Select(attrs={"id":"id_department",'size':1, 'placeholder': u""}))
    username = forms.CharField(label=u'用户名', max_length=100, required=False, widget=forms.TextInput(attrs={"id":"id_username",'size':12, 'placeholder': u""}))
    showmax = forms.CharField(label=u'用户数', max_length=100, required=False, widget=forms.NumberInput(attrs={"id":"id_showmax",'size':12, 'placeholder': u""}))
