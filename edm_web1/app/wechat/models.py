#coding=utf-8
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class WeixinLog(models.Model):
    """
    微信返回的Log日志
    """
    body = models.TextField()
    is_sign = models.BooleanField(u'签名是否正确', default=True)
    type = models.CharField(u'操作类型', max_length=20, help_text=u'统一下单/通知')
    created = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'core_weixin_log'
