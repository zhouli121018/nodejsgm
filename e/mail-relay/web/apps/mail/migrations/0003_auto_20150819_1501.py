# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0002_auto_20150814_1714'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='back_days',
            field=models.IntegerField(default=30, verbose_name='\u90ae\u4ef6\u5907\u4efd\u65e5\u671f'),
        ),
        migrations.AlterField(
            model_name='checksettings',
            name='active_spam_check_time',
            field=models.IntegerField(default=24, help_text='\u5355\u4f4d:\u5c0f\u65f6, \u67d0\u4e2a\u53d1\u4ef6\u4eba\u5728(monitor_time)\u5206\u949f\u5185\u51fa\u73b0(max)\u6b21\u5783\u573e\u90ae\u4ef6\u7279\u5f81\u540e(check_time)\u5c0f\u65f6\u5185\u7684\u90ae\u4ef6\u8fdb\u884c\u5ba1\u6838', verbose_name='\u52a8\u6001\u90ae\u4ef6(\u68c0\u6d4b\u65f6\u95f4check_time)'),
        ),
        migrations.AlterField(
            model_name='checksettings',
            name='active_spam_max',
            field=models.IntegerField(default=1, help_text='\u5355\u4f4d:\u90ae\u4ef6\u5c01\u6570, \u67d0\u4e2a\u53d1\u4ef6\u4eba\u5728(monitor_time)\u5206\u949f\u5185\u51fa\u73b0(max)\u6b21\u5783\u573e\u90ae\u4ef6\u7279\u5f81\u540e(check_time)\u5c0f\u65f6\u5185\u7684\u90ae\u4ef6\u8fdb\u884c\u5ba1\u6838', verbose_name='\u52a8\u6001\u90ae\u4ef6(\u6570\u91cf\u9600\u503cmax)'),
        ),
        migrations.AlterField(
            model_name='checksettings',
            name='active_spam_monitor_time',
            field=models.IntegerField(default=60, help_text='\u5355\u4f4d:\u5206\u949f, \u67d0\u4e2a\u53d1\u4ef6\u4eba\u5728(monitor_time)\u5206\u949f\u5185\u51fa\u73b0(max)\u6b21\u5783\u573e\u90ae\u4ef6\u7279\u5f81\u540e(check_time)\u5c0f\u65f6\u5185\u7684\u90ae\u4ef6\u8fdb\u884c\u5ba1\u6838', verbose_name='\u52a8\u6001\u90ae\u4ef6(\u76d1\u6d4b\u65f6\u95f4monitor_time)'),
        ),
    ]
