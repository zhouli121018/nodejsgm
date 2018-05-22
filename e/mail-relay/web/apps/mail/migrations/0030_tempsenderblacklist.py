# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0030_customer_support_name'),
        ('mail', '0029_spfchecklist'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempSenderBlacklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sender', models.CharField(help_text='\u4e2d\u7ee7\u4e34\u65f6\u53d1\u4ef6\u4eba\u9ed1\u540d\u5355, \u5982\u679c\u53d1\u4ef6\u4eba\u5728\u9ed1\u540d\u5355\u4e2d\uff0c\u62d2\u7edd\u8fde\u63a5\uff0c\u4e0d\u652f\u6301\u6b63\u5219\u8868\u8fbe\u5f0f', max_length=100, verbose_name='\u53d1\u4ef6\u4eba')),
                ('expire_time', models.DateTimeField(verbose_name='\u7fa4\u5c01\u8fc7\u671f\u5929\u6570')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Customer', null=True)),
                ('operater', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
