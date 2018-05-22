# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0052_settings_retry_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='max_same_subject',
            field=models.IntegerField(default=3, help_text='\u5355\u4f4d\uff1a\u5929\u6570\uff0c\u8d85\u8fc7\u8be5\u5929\u6570\u7684\u7f51\u5173\u90ae\u4ef6\u4e0d\u91cd\u8bd5\u53d1\u9001', verbose_name='\u7f51\u5173\u91cd\u8bd5\u5929\u6570'),
        ),
    ]
