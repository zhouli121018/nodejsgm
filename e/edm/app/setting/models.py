#coding=utf-8
from __future__ import unicode_literals

from django.db import models
from app.core.models import Customer
from app.core.configs import NOTIFICATION_TYPE

# Create your models here.

class NoticeSetting(models.Model):
    '''
    通知设置
    '''
    customer = models.ForeignKey(Customer, related_name='settingCustomer01', db_index=True, null=False, blank=False, db_column='customer_id')
    name = models.CharField(u'通知联系人', max_length=50, null=False, blank=False)
    mobile = models.CharField(u'手机', max_length=20, null=True, blank=True)
    email = models.CharField(u'邮箱', max_length=50, null=True, blank=True)
    balance_alert_qty = models.IntegerField(u'余额警戒值', default=10000)

    class Meta:
        managed = False
        db_table = 'core_notice_setting'

    def __unicode__(self):
        return self.name

class NoticeSettingDetail(models.Model):
    '''
    通知设置 明细
    '''
    setting = models.ForeignKey(NoticeSetting, db_index=True, null=False, blank=False, db_column='setting_id', on_delete=models.CASCADE)
    type = models.CharField(u'通知类型', max_length=5, choices=NOTIFICATION_TYPE, null=False, blank=False)
    is_notice = models.BooleanField(u'站内通知', default=True)
    is_email = models.BooleanField(u'邮件', default=True)
    is_sms = models.BooleanField(u'短信', default=True)

    class Meta:
        managed = False
        unique_together = (('setting', 'type'),)
        db_table = 'core_notice_setting_d'

class TokenSetting(models.Model):
    '''
    API Token
    '''
    customer = models.ForeignKey(Customer, related_name='settingCustomer02', null=False, blank=False, db_column='customer_id')
    name = models.CharField(u'名称', max_length=50, null=False, blank=False)
    token = models.CharField(u'Token', max_length=50, null=False, blank=False)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        managed = False
        unique_together = (("customer", "name"),)
        db_table = 'core_token_setting'

    def __unicode__(self):
        return self.name
