# -*- coding: utf-8 -*-
import time

from django.db import models

from app.fail2ban import constants


class Fail2Ban(models.Model):

    name = models.CharField(u"管理员输入的名称", max_length=200, null=True, blank=True)
    proto = models.CharField(u"协议", max_length=50, null=False, blank=True)
    internal = models.IntegerField(u'统计间隔', default=-1)
    block_fail = models.IntegerField(u'验证失败次数', default=-1)
    block_unexists = models.IntegerField(u'验证不存在帐号次数', default=-1)
    block_minute = models.IntegerField(u'禁用时间', default=-1)

    update_time = models.DateTimeField(u"更新时间", null=False, blank=False)
    disabled = models.CharField(u'激活状态', max_length=2, choices=constants.FAIL2BAN_DISABLE, null=False, blank=False, default="-1")

    class Meta:
        managed = False
        db_table = 'ext_fail2ban'

    @property
    def get_proto(self):
        proto_list = self.proto.split(u",")
        if "all" in proto_list:
            return u"所有"
        return self.proto

class Fail2BanTrust(models.Model):

    ip = models.CharField(u"IP", max_length=50, null=False, blank=True)
    name = models.CharField(u"名称", max_length=200, null=True, blank=True)
    disabled = models.CharField(u'激活状态', max_length=2, choices=constants.FAIL2BAN_DISABLE, null=False, blank=False, default="-1")

    class Meta:
        managed = False
        db_table = 'ext_fail2ban_trust'

class Fail2BanBlock(models.Model):

    ip = models.CharField(u"IP", max_length=50, null=False, blank=True)
    name = models.CharField(u"名称", max_length=200, null=True, blank=True)
    expire_time = models.IntegerField(u'过期时间', default=0)
    update_time = models.DateTimeField(u"更新时间", null=False, blank=False)
    disabled = models.CharField(u'激活状态', max_length=2, choices=constants.FAIL2BAN_DISABLE, null=False, blank=False, default="-1")

    class Meta:
        managed = False
        db_table = 'ext_fail2ban_block'

    @property
    def get_expire_time(self):
        try:
            expire = int(self.expire_time)
        except:
            return u"已失效"
        if expire <=0:
            return u"已失效"
        try:
            #settings.py配置的时区比底层晚8小时，先用这个愚蠢的方法保证测试
            t_tuple = time.localtime(expire)
            time_val = time.strftime('%Y-%m-%d %H:%M:%S',t_tuple)
            return u"{}".format(time_val)
        except:
            return u"已失效"
