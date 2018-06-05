# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import smart_str
from app.maintain import choices
from lib.models import ZeroDateTimeField

# ext_sequester_mail
class ExtSquesterMail(models.Model):

    ident = models.CharField(u"邮件标识", max_length=25, null=True, blank=True)
    datetime = ZeroDateTimeField(u"隔离时间", null=False, blank=False)
    sender = models.CharField(u"发件人", max_length=80, null=True, blank=True)
    recipient = models.TextField(u"收件人", null=True, blank=True)
    mailsize = models.IntegerField(u'邮件大小', default=0)
    subject = models.CharField(u"主题", max_length=300, null=True, blank=True)
    attachment = models.SmallIntegerField(u"附件", null=True, blank=True)
    savepath = models.TextField(u"保存路径", null=True, blank=True)
    status = models.CharField(u"主题", max_length=20, default="wait", choices=choices.ISOLATE_STATUS, null=True, blank=True)
    reason = models.CharField(u"隔离原因", max_length=50, null=True, blank=True)
    detail = models.TextField(u"详情", null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'ext_sequester_mail'

    def __str__(self):
        return smart_str(self.ident)

    __repr__ = __str__

    @property
    def get_datetime(self):
        if not self.datetime:
            if self.datetime:
                return self.datetime.strftime('%Y-%m-%d %H:%M:%S')
            return "unknown"
        return self.datetime.strftime('%Y-%m-%d %H:%M:%S')
