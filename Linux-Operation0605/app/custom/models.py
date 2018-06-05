# -*- coding: utf-8 -*-
import time

from django.db import models

class CustomKKServerToken(models.Model):

    imap_id = models.IntegerField(u'imap_id', null=False)
    task_id = models.CharField(u'任务ID', max_length=100, null=False, blank=False)
    mailbox = models.CharField(u'邮箱', max_length=200, null=False, blank=False)
    token = models.CharField(u'token', max_length=100, null=False, blank=False)

    expire_time = models.DateTimeField(u"过期时间", null=False, blank=False)
    update_time = models.DateTimeField(u"更新时间", null=False, blank=False)

    class Meta:
        managed = False
        db_table = 'custom_kkserver_login'
