# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
from django.db import models
from django.utils.translation import ugettext_lazy as _
from app.core.models import Domain

EXT_LIST_TYPE = (
    ('general', u'普通邮件列表'),
    ('dept', u'部门邮件列表'),
    ('sys', u'系统邮件列表')
)
EXT_LIST_PERMISSION = (
    ('public', u'公开列表'),
    ('private', u'私有列表'),
    ('domain', u'本域公共列表')
)

EXT_LIST_STATUS = (
    ('-1', u'正常'),
    ('1', u'禁用'),
)

EXT_LIST_MEM_PERMIT = (
    ('1', u'收发'),
    ('-1', u'只发'),
    ('0', u'只收'),
)

class ExtList(models.Model):
    listname = models.CharField(_(u'邮件列表名称'), max_length=35, blank=True, null=True)
    address = models.CharField(_(u'邮件列表地址'), max_length=200, db_index=True, null=True, blank=True)
    listtype = models.CharField(_(u'邮件列表类型'), max_length=10, choices=EXT_LIST_TYPE, default='general')
    domain_id = models.IntegerField(u'所属域名ID', default=0)
    dept_id = models.IntegerField(u'部门ID', default=0, help_text=u'类型为“部门邮件列表”对应的部门ID')
    permission = models.CharField(_(u'权限类型'), max_length=10, choices=EXT_LIST_PERMISSION, default='public',
                                  help_text=u'设置为公开列表，所有人都可以向此邮件列表发送邮件；'
                                            u'设置为私有列表,只有设置了发送权限的邮箱才可向此邮件列表发送邮件；'
                                            u'设置为本域公共列表 ,只有同服务器的邮箱才可向此邮件列表发送邮件。')
    showorder = models.IntegerField(_(u'显示顺序'), default=0)
    description = models.TextField(_(u'说明信息'), null=True, blank=True)
    disabled = models.CharField(_(u'列表状态'), max_length=2, choices=EXT_LIST_STATUS, default='-1')

    class Meta:
        managed = False
        db_table = 'ext_list'
        verbose_name = _(u'邮件列表信息表')
        verbose_name_plural = _(u'邮件列表信息表')

    @property
    def domain(self):
        obj = Domain.objects.filter(id=self.domain_id).first()
        return obj and obj.domain or None

    @property
    def is_everyone(self):
        name = self.address and "@".join(
            self.address.split("@")[:-1]) or ""
        if name=='everyone':
            return True
        return False

class ExtListMember(models.Model):
    domain_id = models.IntegerField(u'所属域名ID', default=0)
    list_id = models.IntegerField(u'列表ID', default=0, db_index=True)
    address = models.CharField(_(u'邮件地址'), max_length=80, null=True, blank=True, help_text=u'如不填写邮箱后缀，将自动加上本域域名')
    permit = models.CharField(_(u'地址权限'), max_length=2, choices=EXT_LIST_MEM_PERMIT, default='-1')
    name = models.CharField(_(u'昵称'), max_length=200, blank=True, null=True)
    update_time = models.IntegerField(_(u'修改时间'), default=0)

    class Meta:
        managed = False
        db_table = 'ext_list_member'
        verbose_name = _(u'邮件列表成员表')
        verbose_name_plural = _(u'邮件列表成员表')

    @property
    def updated(self):
        if self.update_time:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.update_time))
        return '-'

    def set_domain_id(self, list_id):
        obj = ExtList.objects.get(id=list_id)
        self.domain_id = obj.domain_id
