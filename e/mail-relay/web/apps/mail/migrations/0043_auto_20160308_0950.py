# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0042_noticesettings_review_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='noticesettings',
            name='bulk_count',
            field=models.IntegerField(default=200, help_text='\u7528\u6237\u5f53\u5929\u4e2d\u7ee7\u7684\u62d2\u7edd\u6570\u91cf\u9600\u503c\uff0c\u5982\u679c\u8d85\u8fc7\u8be5\u503c\uff0c\u5219\u53d1\u76f8\u5e94\u901a\u77e5', verbose_name='\u7fa4\u53d1\u6570\u91cf\u9600\u503c'),
        ),
        migrations.AlterField(
            model_name='noticesettings',
            name='bulk_content',
            field=models.TextField(help_text='\u7528\u6237\u7fa4\u53d1\u90ae\u4ef6\u7684\u65f6\u5019\u901a\u77e5\u5ba2\u6237\u548c\u5bf9\u5e94\u7684\u6280\u672f\u652f\u6301,\u652f\u6301\u53d8\u91cf: {count}\u8868\u793a\u62d2\u7edd\u6570\u91cf', verbose_name='\u7fa4\u53d1\u90ae\u4ef6\u901a\u77e5'),
        ),
    ]
