# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0049_auto_20160317_1701'),
    ]

    operations = [
        migrations.AddField(
            model_name='noticesettings',
            name='jam_content',
            field=models.TextField(help_text='\u5b9e\u65f6\u76d1\u63a7\u670d\u52a1\u5668\u5904\u7406\u72b6\u6001\uff0c\u5f53\u4e2d\u7ee7\u68c0\u6d4b\u6570\uff0b\u4e2d\u7ee7\u4f20\u8f93\u6570\uff0b\u7f51\u5173\u68c0\u6d4b\u6570\u8d85\u8fc7\u9600\u503c\u65f6\uff0c\u53d1\u9001\u901a\u77e5,\u652f\u6301\u53d8\u91cf: {count}\u8868\u793a\u603b\u6570,{relay_check}\u8868\u793a\u4e2d\u7ee7\u68c0\u6d4b\u6570,{relay_dispatch}\u8868\u793a\u4e2d\u7ee7\u4f20\u8f93\u6570,{relay_check}\u8868\u793a\u4e2d\u7ee7\u68c0\u6d4b\u6570', null=True, verbose_name='\u670d\u52a1\u5668\u62e5\u5835\u901a\u77e5', blank=True),
        ),
        migrations.AddField(
            model_name='noticesettings',
            name='jam_count',
            field=models.IntegerField(default=200, help_text='\u670d\u52a1\u5668\u9700\u5904\u7406\u7684\u90ae\u4ef6\u5c01\u6570\uff08\u4e2d\u7ee7\u68c0\u6d4b\u6570\uff0b\u4e2d\u7ee7\u4f20\u8f93\u6570\uff0b\u7f51\u5173\u68c0\u6d4b\u6570\uff09\uff0c\u5f53\u8d85\u8fc7\u8be5\u503c\u65f6\uff0c\u53d1\u9001\u76f8\u5e94\u901a\u77e5', verbose_name='\u62e5\u5835\u9600\u503c'),
        ),
        migrations.AddField(
            model_name='noticesettings',
            name='jam_interval',
            field=models.IntegerField(default=60, help_text='\u5355\u4f4d\uff1a\u5206\u949f\uff0c\u670d\u52a1\u5668\u62e5\u5835\u901a\u77e5\u53d1\u9001\u95f4\u9694\u65f6\u95f4', verbose_name='\u670d\u52a1\u5668\u62e5\u5835\u901a\u77e5\u95f4\u9694'),
        ),
    ]
