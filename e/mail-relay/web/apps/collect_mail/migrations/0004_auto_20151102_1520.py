# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collect_mail', '0003_remove_deliverlog_mx_record'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistics',
            name='error_type_1',
            field=models.IntegerField(default=0, verbose_name='\u8fde\u63a5\u9519\u8bef'),
        ),
        migrations.AddField(
            model_name='statistics',
            name='error_type_2',
            field=models.IntegerField(default=0, verbose_name='\u4e0d\u5b58\u5728\u9519\u8bef'),
        ),
        migrations.AddField(
            model_name='statistics',
            name='error_type_3',
            field=models.IntegerField(default=0, verbose_name='\u5176\u4ed6\u9519\u8bef'),
        ),
        migrations.AddField(
            model_name='statistics',
            name='error_type_4',
            field=models.IntegerField(default=0, verbose_name='\u8d85\u5927/\u6ee1\u7684\u90ae\u4ef6'),
        ),
        migrations.AddField(
            model_name='statistics',
            name='error_type_5',
            field=models.IntegerField(default=0, verbose_name='\u5783\u573e\u90ae\u4ef6'),
        ),
        migrations.AddField(
            model_name='statistics',
            name='error_type_6',
            field=models.IntegerField(default=0, verbose_name='\u4e0d\u91cd\u8bd5\u90ae\u4ef6'),
        ),
        migrations.AddField(
            model_name='statistics',
            name='error_type_7',
            field=models.IntegerField(default=0, verbose_name='spf\u90ae\u4ef6'),
        ),
    ]
