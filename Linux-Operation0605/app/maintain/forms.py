# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import time
from django import forms
from app.maintain import choices
from app.core.models import CoreConfig, Mailbox
from django.utils.translation import ugettext_lazy as _

from lib import validators
from lib.forms import BaseFied, DotDict
from lib.tools import clear_redis_cache

class MailSearchForm(forms.Form):
    mail_status = forms.ChoiceField(label=u'状态', choices=choices.ISOLATE_STATUS_R, required=False, initial="wait")
    mail_sender = forms.CharField(label=u'发件人', max_length=80, required=False, widget=forms.TextInput(attrs={'size':12, 'placeholder': u""}))
    mail_sender_not = forms.CharField(label=u'发件人不包含', max_length=80, required=False, widget=forms.TextInput(attrs={'size':12, 'placeholder': u""}))
    mail_recipient = forms.CharField(label=u'收件人', max_length=80, required=False, widget=forms.TextInput(attrs={'size':12}))
    mail_subject = forms.CharField(label=u'主题', max_length=80, required=False, widget=forms.TextInput(attrs={'size':12}))
    mail_reason = forms.CharField(label=u'隔离原因', max_length=50, required=False, widget=forms.TextInput(attrs={'size':12}))
    mail_detail = forms.CharField(label=u'详情', max_length=80, required=False, widget=forms.TextInput(attrs={'size':12}))


class BackupSetForm(forms.Form):

    DATA_TYPE_CHOICES = choices.DATA_TYPE_CHOICES
    BACKUP_TYPE = choices.BACKUP_TYPE
    BACKUP_MONTH = choices.BACKUP_MONTH
    BACKUP_DAY = choices.BACKUP_DAY
    BACKUP_WEEK = choices.BACKUP_WEEK
    BACKUP_HOUR = choices.BACKUP_HOUR
    BACKUP_MINUTE = choices.BACKUP_MINUTE

    path = forms.CharField(label=u'保存路径', max_length=300, required=True, initial=u"/usr/local/u-mail/data/backup/",
                           help_text=u"注：备份数据的保存路径，请填写绝对路径；默认为“/usr/local/u-mail/data/backup/”！")
    data = forms.MultipleChoiceField(label=u'数据类型', required=True, choices=DATA_TYPE_CHOICES, initial=["database", "maildata"],
                                     help_text=u"可多选，按住Ctrl多选。", widget=forms.CheckboxSelectMultiple,) #widget=forms.CheckboxSelectMultiple,
    count = forms.IntegerField(label=u"保留备份数量", initial=10, required=True, help_text=u"留注：当备份的数据超过此限制时，将会删除旧的备份数据！ ")
    # 备份周期
    type = forms.ChoiceField(label=u"备份周期", required=True, choices=BACKUP_TYPE, initial="month")
    cycle = forms.IntegerField(label=u"Cycle", required=True, initial=1)
    # 备份时间
    month = forms.ChoiceField(label=u"Month", required=False, choices=BACKUP_MONTH)
    date =  forms.ChoiceField(label=u"Day", required=False, choices=BACKUP_DAY)
    week =  forms.ChoiceField(label=u"Week", required=False, choices=BACKUP_WEEK)
    hour =  forms.ChoiceField(label=u"Hour", required=False, choices=BACKUP_HOUR)
    minute =  forms.ChoiceField(label=u"Minute", required=False, choices=BACKUP_MINUTE)

    def clean_path(self):
        data = self.cleaned_data['path'].strip()
        if not data:
            raise forms.ValidationError(_(u"请填写保存路径"))
        return data

    def clean_count(self):
        data = self.cleaned_data['count']
        data = data and int(data) or 0
        if data<=0:
            raise forms.ValidationError(_(u"备份数量必须大于等于1"))
        return data

    def clean_cycle(self):
        data = self.cleaned_data['cycle']
        data = data and int(data) or 0
        if data<=0:
            raise forms.ValidationError(_(u"备份周期必须大于等于1"))
        return data

    def save(self):
        path = self.cleaned_data['path']
        data = self.cleaned_data['data']
        count = self.cleaned_data['count']
        ltype = self.cleaned_data['type']
        cycle = self.cleaned_data['cycle']

        week=""
        month=""
        date=""
        hour=""
        if ltype == "hour":
            minute = self.cleaned_data['minute']
        elif ltype == "day":
            minute = self.cleaned_data['minute']
            hour = self.cleaned_data['hour']
        elif ltype == "week":
            minute = self.cleaned_data['minute']
            hour = self.cleaned_data['hour']
            week = self.cleaned_data['week']
        elif ltype == "month":
            minute = self.cleaned_data['minute']
            hour = self.cleaned_data['hour']
            date = self.cleaned_data['date']
        else:
            minute = self.cleaned_data['minute']
            hour = self.cleaned_data['hour']
            date = self.cleaned_data['date']
            month = self.cleaned_data['month']
        CoreConfig.saveFuction(function="auto_backup", enabled=None, param=json.dumps({
            "path": path, "data": data, "count": count, "cycle": cycle, "type": ltype,
            "month": month, "date": date, "week": week, "hour": hour, "minute": minute,
        }), withenabled=False)

        clear_redis_cache()
