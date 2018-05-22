# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('core', '0012_auto_20151105_1442'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='\u8bf7\u4f7f\u7528\u82f1\u6587\u540d\u79f0', max_length=20, verbose_name='\u6743\u9650\u540d\u79f0')),
                ('is_nav', models.BooleanField(default=True, verbose_name='\u662f\u5426\u4e3a\u5bfc\u822a')),
                ('nav_name', models.CharField(help_text='\u5982\u679c\u4e0d\u662f\u5bfc\u822a\uff0c\u53ef\u4e0d\u7528\u586b\u5199', max_length=20, verbose_name='\u5bfc\u822a\u540d\u79f0')),
                ('url', models.CharField(max_length=100, null=True, verbose_name='\u76ee\u5f55url', blank=True)),
                ('is_default', models.BooleanField(default=False, help_text='\u5982\u679c\u662f\u9ed8\u8ba4\u6743\u9650\uff0c\u6dfb\u52a0\u540e\u4e0d\u80fd\u901a\u8fc7\u9875\u9762\u4fee\u6539', verbose_name='\u662f\u5426\u4e3a\u9ed8\u8ba4\u6743\u9650')),
                ('order', models.IntegerField(default=1, help_text='\u8d8a\u5c0f\u6392\u5728\u8d8a\u524d\u9762', verbose_name='\u5bfc\u822a\u987a\u5e8f')),
                ('parent', models.ForeignKey(related_name='children', to='core.MyPermission')),
                ('permission', models.ForeignKey(to='auth.Permission')),
            ],
        ),
    ]
