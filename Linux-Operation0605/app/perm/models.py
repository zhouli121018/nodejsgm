# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

class MyPermission(models.Model):
    '''
    自定义权限表
    '''
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    permission = models.ForeignKey(Permission, null=True, blank=True, db_index=True)
    name = models.CharField(u'权限名称', max_length=50, unique=True, null=False, blank=False, help_text=u'请使用英文名称，只能使用数字、字母以及特殊字符（._-）')
    is_nav = models.BooleanField(u'是否为导航', default=True)
    nav_name = models.CharField(u'导航名称', max_length=50, null=False, blank=False, help_text=u'如果不是导航，可不用填写')
    url = models.CharField(u'目录url', max_length=150, null=True, blank=True, help_text=u'注意：比如/p/123/, 请维护成/p/modify/')
    is_default = models.BooleanField(u'是否为默认权限', default=False)
    order_id = models.IntegerField(u'导航顺序', default=1, help_text=u'越小排在越前面')

    def __unicode__(self):
        return u'{}({})'.format(self.name, self.nav_name)

    def per(self):
        permission = self.permission
        return '{}.{}'.format(permission.content_type.app_label, permission.codename)

    def nav_children(self):
        return self.children.filter(is_nav=True)

    def save(self, *args, **kwargs):
        if self.permission:
            p = self.permission
            p.codename = self.name
            p.name = self.name
            p.save()
        else:
            content_type, _ = ContentType.objects.get_or_create(app_label='perm', model='mypermission')
            permission, _ = Permission.objects.get_or_create(
                codename=self.name,
                name=self.name,
                content_type=content_type
            )
            setattr(self, 'permission', permission)
        super(MyPermission, self).save(*args, **kwargs)

    def get_perm(self):
        return '%s.%s' % (self.permission.content_type.app_label, self.permission.codename)

    class Meta:
        managed = False
        db_table = 'perm_mypermission'