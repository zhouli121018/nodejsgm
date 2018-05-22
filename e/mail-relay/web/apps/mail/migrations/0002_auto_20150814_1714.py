# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='checksettings',
            name='active_spam_check_time',
            field=models.IntegerField(default=0, help_text='\u5355\u4f4d:\u5c0f\u65f6', verbose_name='\u9ad8\u5371\u90ae\u4ef6\u76d1\u6d4b\u65f6\u95f4'),
        ),
        migrations.AddField(
            model_name='checksettings',
            name='active_spam_max',
            field=models.IntegerField(default=0, help_text='\u5355\u4f4d:\u90ae\u4ef6\u5c01\u6570', verbose_name='\u9ad8\u5371\u90ae\u4ef6\u6570\u91cf\u9600\u503c'),
        ),
        migrations.AddField(
            model_name='checksettings',
            name='active_spam_monitor_time',
            field=models.IntegerField(default=0, help_text='\u5355\u4f4d:\u5206\u949f', verbose_name='\u9ad8\u5371\u90ae\u4ef6\u76d1\u6d4b\u65f6\u95f4'),
        ),
    ]
