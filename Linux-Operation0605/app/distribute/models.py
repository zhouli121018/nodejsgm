# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from app.core import constants


class ProxyServerConfig(models.Model):
    config_name = models.CharField(u"配置名称", max_length=40, null=False, blank=False, unique=True)
    config_data = models.CharField(u"配置值", max_length=250, null=False, blank=False)
    ext = models.CharField(u'备注', max_length=100, null=False, blank=False, help_text=u"指明数据的用途")
    pwd = models.CharField(u'授权密码', max_length=128, null=False, blank=False, default="0", help_text=u"分布式开关使用到的授权码")

    class Meta:
        managed = False
        db_table = "proxy_server_config"

    def __str__(self):
        return self.ext

    @staticmethod
    def proxy_open():
        obj, _created = ProxyServerConfig.objects.get_or_create(config_name="proxy_open")
        if _created:
            obj.config_data = "1"
            obj.ext = "分布式开关"
            obj.save()
        return obj

    @staticmethod
    def local_ip():
        obj, _created = ProxyServerConfig.objects.get_or_create(config_name="local_ip")
        if _created:
            obj.config_data = ""
            obj.ext = "本机IP"
            obj.save()
        return obj

class ProxyServerList(models.Model):
    id = models.AutoField(primary_key=True, db_column='server_num')
    server_name = models.CharField(u'服务器名称', max_length=120, null=False, blank=False)
    server_ip = models.CharField(u'服务器IP', max_length=20, null=False, blank=False)
    is_master = models.BooleanField(u'是否主服务器', default=False)
    disabled = models.CharField(u'状态', max_length=1, choices=constants.PROXY_CONFIG_DISABLED, null=False, blank=False, default="-1")

    class Meta:
        managed = False
        db_table = "proxy_server_list"

    def __str__(self):
        return self.server_name

class ProxyServerStatus(models.Model):
    id = models.AutoField(primary_key=True, db_column='server_num')
    status_conn = models.CharField(u'本服发起状态', max_length=20, choices=constants.PROXY_SERVER_STATUS, null=True, blank=True)
    status_recv = models.CharField(u'本服接收状态', max_length=20, choices=constants.PROXY_SERVER_STATUS, null=True, blank=True)
    reject_reason = models.CharField(u'拒绝原因', max_length=500, null=True, blank=True)
    last_update = models.DateTimeField(u'更新时间', null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = "proxy_server_status"

    @property
    def server(self):
        return ProxyServerList.objects.filter(pk=self.pk).first()

    def __str__(self):
        return self.server and self.server.server_name or ""


class ProxyRouter(models.Model):
    id = models.AutoField(primary_key=True, db_column='router_id')
    server_num = models.IntegerField(u'服务器', default=0)
    acct_idx = models.IntegerField(u'唯一编号', default=0)

    class Meta:
        managed = False
        db_table = "proxy_router_table"

class ProxyAccount(models.Model):
    id = models.AutoField(primary_key=True, db_column='acct_id')
    router_id = models.IntegerField(u"ProxyRouter", default=0, db_index=True)
    birth_server = models.IntegerField("账号创建服务器", default=0, db_index=True)
    mailbox_id = models.IntegerField(u"MailBox", default=0)
    mailbox = models.CharField(u"发件人邮箱", null=False, blank=False, max_length=200, unique=True)
    acct_server = models.IntegerField("账号服务器", default=0, db_index=True)
    disabled = models.CharField(u'状态', max_length=1, choices=constants.PROXY_CONFIG_DISABLED, null=False, blank=False, default="-1")

    class Meta:
        managed = False
        db_table = "proxy_account"
        index_together = ( ("acct_server", "mailbox_id") )

class ProxyAccountMove(models.Model):
    acct_id = models.IntegerField("ProxyAccount", default=0, unique=True)
    mailbox_id = models.IntegerField(u"MailBox", default=0)
    mailbox = models.CharField(u"发件人邮箱", null=False, blank=False, max_length=200, unique=True)
    old_mailbox = models.CharField(u"新邮箱名字", null=True, blank=True, max_length=200, default="", db_index=True)
    from_server = models.IntegerField(u"源服务器", default=0)
    from_ip = models.CharField(u"源服务器IP", null=True, blank=True, max_length=20, default="")
    target_server = models.IntegerField(u"目标服务器", default=0)
    target_ip = models.CharField(u"目标服务器IP", null=False, blank=False, max_length=20)
    move_type = models.CharField(u'移动方式', null=False, blank=False, max_length=20, choices=constants.PROXY_MOVE_TYPE, default="to")
    sync_mail = models.BooleanField(u"是否同步邮件", default=False)
    status = models.CharField(u"状态", default="init", null=False, blank=False, max_length=20, choices=constants.PROXY_MOVE_STATUS)
    desc_msg = models.TextField(u"描述", null=True, blank=True)
    last_update = models.DateTimeField(u'更新时间', null=True, auto_now=True)
    data = models.BinaryField(u"迁移的数据", null=True, blank=True)

    class Meta:
        managed = False
        db_table = "proxy_account_move"
        unique_together = (
            ('from_server', 'mailbox_id'),
            ('from_server', 'mailbox'),
        )

    @property
    def from_server_obj(self):
        return ProxyServerList.objects.filter(pk=self.from_server).first()

    @property
    def target_server_obj(self):
        return ProxyServerList.objects.filter(pk=self.target_server).first()

    @property
    def can_mdf(self):
        if self.move_type == "to" and self.status not in ("init", "wait", "sync", "accept", "ready", "backup"):
            return False
        if self.move_type == "from" and self.status not in ("create", "done", "imap_recv"):
            return False
        return True

    @property
    def can_delete(self):
        if self.status not in ("finish", "unvalid"):
            return False
        return True
