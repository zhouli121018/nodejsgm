# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_notification_is_notice'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mail', '0067_auto_20160507_2302'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerSenderBlacklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sender', models.CharField(help_text='\u53d1\u4ef6\u4eba\u9ed1\u540d\u5355\uff0c\u5982\u679c\u53d1\u4ef6\u4eba\u5728\u9ed1\u540d\u5355\u4e2d\uff0c\u8df3\u8fc7\u540e\u9762\u6240\u6709\u7684\u7f51\u5173\u68c0\u6d4b\uff0c\u63a5\u62d2\u7edd\u3002', max_length=150, verbose_name='\u53d1\u4ef6\u4eba')),
                ('is_global', models.BooleanField(default=False, help_text='\u5168\u5c40\u9ed1\uff0c\u662f\u5bf9\u6240\u6709\u5ba2\u6237\u751f\u6548\u3002\u5ba2\u6237\u9ed1\uff0c\u4ec5\u4ec5\u5bf9\u8fd9\u4e2a\u5ba2\u6237\u751f\u6548', verbose_name='\u662f\u5426\u4e3a\u5168\u5c40\u53d8\u91cf')),
                ('is_domain', models.BooleanField(default=False, help_text='\u5f53\u9009\u4e2d\u65f6\uff0c\u6574\u4e2a\u57df\u540d\u90fd\u4e3a\u9ed1\u540d\u5355\uff0c\u9ed8\u8ba4\u4e0d\u9009\u4e2d', verbose_name='\u662f\u5426\u4e3a\u57df\u540d')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('operate_time', models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True)),
                ('creater', models.ForeignKey(related_name='creater110', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('customer', models.ForeignKey(blank=True, to='core.Customer', null=True)),
                ('operater', models.ForeignKey(related_name='operater110', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
