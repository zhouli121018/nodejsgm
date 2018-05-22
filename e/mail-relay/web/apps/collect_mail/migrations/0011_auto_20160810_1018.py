# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collect_mail', '0010_auto_20160203_1435'),
        ('core', '__first__'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistics',
            name='mail_count',
            field=models.IntegerField(default=0, verbose_name='\u90ae\u4ef6\u603b\u6570'),
        ),
        migrations.AddField(
            model_name='statistics',
            name='spam_count',
            field=models.IntegerField(default=0, verbose_name='\u5783\u573e\u90ae\u4ef6\u6570'),
        ),
        migrations.AddField(
            model_name='statistics',
            name='spam_rate',
            field=models.FloatField(default=0, verbose_name='\u8fc7\u6ee4\u7387'),
        ),
    ]
