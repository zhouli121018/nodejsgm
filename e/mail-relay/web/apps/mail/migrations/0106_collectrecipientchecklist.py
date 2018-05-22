# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mail', '0105_auto_20171017_1107'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectRecipientChecklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u7f51\u5173\u6536\u4ef6\u4eba\u5f3a\u5236\u68c0\u6d4b\u540d\u5355, \u5982\u679c\u6536\u4ef6\u4eba\u5728\u767d\u540d\u5355\u4e2d\uff0c\u8be5\u53d1\u4ef6\u4eba\u7684\u6240\u6709\u90ae\u4ef6\u5fc5\u987b\u5f3a\u5236\u68c0\u6d4b', unique=True, max_length=50, verbose_name='\u6536\u4ef6\u4eba')),
                ('is_regex', models.BooleanField(default=False, verbose_name='\u662f\u5426\u652f\u6301\u6b63\u5219')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('operate_time', models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True)),
                ('creater', models.ForeignKey(related_name='crc_cr', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('operater', models.ForeignKey(related_name='crc_or', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
