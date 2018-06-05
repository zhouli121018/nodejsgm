# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import models
from django.template import Template, Context
from app.core.models import Domain
from app.domain import constants
from lib.formats import dict_compatibility, safe_format


class Signature(models.Model):
    """
    个人签名设置
    """
    domain_id = models.IntegerField(u'域名ID', default=0, null=False, blank=False, db_index=True)
    mailbox_id = models.IntegerField(u'邮箱ID', default=0, null=False, blank=False, db_index=True)

    type = models.CharField('类型', max_length=20, null=True, blank=False)
    caption = models.CharField('标题', max_length=35, null=True, blank=False)
    content = models.TextField(u"内容", null=True, blank=True)
    default = models.CharField('新邮件默认', max_length=10, null=False, blank=False)
    refw_default = models.CharField('回复转发时的默认签名', max_length=10, null=False, blank=False)

    class Meta:
        db_table = 'wm_signature'
        managed = False

class SecretMail(models.Model):

    secret_grade = models.CharField(u'状态', max_length=1, choices=constants.DOMAIN_SECRET_GRADE_ALL, default=constants.DOMAIN_SECRET_GRADE_1, null=False, blank=False)
    mailbox_id = models.IntegerField(u'邮箱ID', default=0, null=False, blank=False, db_index=True)

    class Meta:
        db_table = 'ext_secret_mail'
        managed = False
