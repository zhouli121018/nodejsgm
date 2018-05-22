# coding=utf-8
from __future__ import unicode_literals
from django.db import models
from app.core.models import Customer


class Suggest(models.Model):
    name = models.CharField(u"路径名称", unique=True, max_length=50)
    path = models.CharField(u'URL', max_length=200,unique=True, help_text=u'URI地址')

    class Meta:
        managed = False
        db_table = 'page_suggest'

class SuggestDetail(models.Model):
    suggest = models.ForeignKey(Suggest, db_index=True, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, related_name='customer_suggest_rel', db_index=True)
    remark = models.TextField(u'建议', null=True, blank=True)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'page_suggest_d'
