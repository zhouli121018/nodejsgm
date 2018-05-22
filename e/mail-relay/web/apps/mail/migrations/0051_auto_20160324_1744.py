# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0050_auto_20160321_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keywordblacklist',
            name='collect',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u7f51\u5173'),
        ),
        migrations.AlterField(
            model_name='noticesettings',
            name='jam_content',
            field=models.TextField(help_text='\u5b9e\u65f6\u76d1\u63a7\u670d\u52a1\u5668\u5904\u7406\u72b6\u6001\uff0c\u5f53\u4e2d\u7ee7\u68c0\u6d4b\u6570\uff0b\u4e2d\u7ee7\u4f20\u8f93\u6570\uff0b\u7f51\u5173\u68c0\u6d4b\u6570\u8d85\u8fc7\u9600\u503c\u65f6\uff0c\u53d1\u9001\u901a\u77e5,\u652f\u6301\u53d8\u91cf: {count}\u8868\u793a\u603b\u6570,{relay_check}\u8868\u793a\u4e2d\u7ee7\u68c0\u6d4b\u6570,{relay_dispatch}\u8868\u793a\u4e2d\u7ee7\u4f20\u8f93\u6570,{collect_check}\u8868\u793a\u4e2d\u7ee7\u68c0\u6d4b\u6570', null=True, verbose_name='\u670d\u52a1\u5668\u62e5\u5835\u901a\u77e5', blank=True),
        ),
        migrations.AlterField(
            model_name='senderblacklist',
            name='direct_reject',
            field=models.BooleanField(default=False, verbose_name='\u4e2d\u7ee7,\u662f\u5426\u4e0d\u7528\u5ba1\u6838\uff0c\u76f4\u63a5\u62d2\u7edd'),
        ),
        migrations.AlterField(
            model_name='subjectkeywordblacklist',
            name='collect',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u7f51\u5173'),
        ),
        migrations.AlterField(
            model_name='subjectkeywordblacklist',
            name='direct_reject',
            field=models.BooleanField(default=False, verbose_name='\u4e2d\u7ee7,\u662f\u5426\u4e0d\u7528\u5ba1\u6838\uff0c\u76f4\u63a5\u62d2\u7edd'),
        ),
    ]
