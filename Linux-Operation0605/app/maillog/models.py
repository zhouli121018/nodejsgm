# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
import json
from django.db import models
from django.template import Template, Context
from app.core.models import Domain
from lib.formats import dict_compatibility, safe_format

from app.maillog import constants


class MailLog(models.Model):
    """
    邮件收发log
    """
    main_id = models.CharField(u'任务主ID', max_length=30, null=False, blank=False)
    domain_id = models.IntegerField(u"域名ID", default=0, db_index=True, null=False, blank=False,help_text=u"域名ID")
    mailbox_id = models.IntegerField(u"邮箱ID", default=0, db_index=True, null=False, blank=False,help_text=u"邮箱ID")
    type = models.CharField(u'发送类型', max_length=10, choices=constants.MAILLOG_TYPE, default='out', null=False, blank=False)
    send_mail = models.CharField(u'发信人', max_length=100, blank=False)
    recv_mail = models.CharField(u'收信人', db_column='rcv_mail', max_length=100, blank=False)
    subject = models.CharField(u'主题', max_length=200, blank=False)
    size = models.IntegerField(u"邮件大小", default=0, db_index=False, blank=False,help_text=u"邮件大小")
    attachment = models.CharField(u'附件名称', max_length=3000, blank=False)
    attachment_size = models.IntegerField(u"附件大小", default=0, db_index=False, blank=False, help_text=u"附件大小")
    result = models.CharField(u'结果', max_length=2, choices=constants.MAILLOG_RESULT, default=-1, null=False, blank=False)
    description = models.TextField(u"描述", null=True, blank=True)
    send_time = models.DateTimeField(u"发信时间", null=True, blank=False)
    recv_time = models.DateTimeField(u" 收信时间", null=True, blank=False)
    senderip = models.CharField(u'发信IP', max_length=20, null=True, blank=False)
    status = models.CharField(u'收发状态', max_length=20, null=True, blank=False)
    rcv_server = models.CharField(u'接收服务器', max_length=100, null=True, blank=False)
    folder = models.CharField(u'投递位置', max_length=100, null=True, blank=False)
    remark = models.CharField(u'备注', max_length=200, null=True, blank=False)

    class Meta:
        db_table = 'core_mail_log'
        managed = False

    @property
    def get_type(self):
        if self.type == "in":
            return u"收信"
        else:
            return u"发信"

    @property
    def get_result(self):
        return str(self.result)

    @property
    def get_time(self):
        if not self.recv_time:
            if self.send_time:
                return self.send_time.strftime('%Y-%m-%d %H:%M:%S')
            return "unknown"
        return self.recv_time.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def get_username(self):
        if self.type == "in":
            l = self.recv_mail.split("@")
        else:
            l = self.send_mail.split("@")
        if l:
            return l[0]
        return "unknown"

    @property
    def get_attach_size(self):
        size = round(int(self.attachment_size)*1.0/(1024*1024),2)
        return size

class LogReport(models.Model):
    domain_id = models.IntegerField(u"域名ID", default=0, db_index=True, null=False, blank=False,help_text=u"域名ID")
    mailbox_id = models.IntegerField(u"邮箱ID", default=0, db_index=True, null=False, blank=False,help_text=u"邮箱ID")
    type = models.CharField(u'记录类型', max_length=10, choices=constants.MAILLOG_TYPE, default='out', null=False, blank=False)
    key = models.CharField(u'键值', max_length=200, blank=False)
    data = models.CharField(u'数据', max_length=2000, blank=False, null=True)
    last_update = models.DateTimeField(u"更新时间", null=False, blank=False)

    class Meta:
        db_table = 'ext_log_report'
        managed = False

    @staticmethod
    def get_cache(domain_id,mailbox_id,type,key):
        obj = LogReport.objects.filter(domain_id=domain_id,mailbox_id=mailbox_id,type=type,key=key).first()
        if not obj or not obj.data:
            return {}
        data = json.loads(obj.data)
        return data

    @staticmethod
    def save_cache(domain_id,mailbox_id,type,key,data):
        obj, _created = LogReport.objects.get_or_create(domain_id=domain_id,mailbox_id=mailbox_id,type=type,key=key)

        data = json.dumps( data )
        obj.domain_id = domain_id
        obj.mailbox_id = mailbox_id
        obj.type = type
        obj.key = key
        obj.data = data
        obj.last_update = time.strftime("%Y-%m-%d %H:%M:%S")
        obj.save()

class LogActive(models.Model):

    domain_id = models.IntegerField(u"域名ID", default=0, db_index=True, null=False, blank=False,help_text=u"域名ID")
    mailbox_id = models.IntegerField(u"邮箱ID", default=0, db_index=True, null=False, blank=False,help_text=u"邮箱ID")
    key = models.CharField(u'键值', max_length=200, blank=False)

    total_count = models.IntegerField(u"总数量", default=0, db_index=True, null=False, blank=False,help_text=u"总数量")
    total_flow = models.IntegerField(u"总流量", default=0, db_index=True, null=False, blank=False,help_text=u"总流量")

    in_count = models.IntegerField(u"收信数量", default=0, db_index=True, null=False, blank=False,help_text=u"收信数量")
    in_flow = models.IntegerField(u"收信流量", default=0, db_index=True, null=False, blank=False,help_text=u"收信流量")

    success_count = models.IntegerField(u"成功数量", default=0, db_index=True, null=False, blank=False,help_text=u"成功数量")
    success_flow = models.IntegerField(u"成功流量", default=0, db_index=True, null=False, blank=False,help_text=u"成功流量")

    spam_count = models.IntegerField(u"垃圾数量", default=0, db_index=True, null=False, blank=False,help_text=u"垃圾数量")
    spam_flow = models.IntegerField(u"垃圾流量", default=0, db_index=True, null=False, blank=False,help_text=u"垃圾流量")

    spam_ratio = models.CharField(u'垃圾比率', max_length=10, blank=False)
    success_ratio = models.CharField(u'成功比率', max_length=10, blank=False)

    class Meta:
        db_table = 'ext_log_active'
        managed = False
