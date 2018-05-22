# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0061_auto_20160413_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='keywordblacklist',
            name='parent',
            field=models.ForeignKey(related_name='children', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='mail.KeywordBlacklist', null=True),
        ),
        migrations.AlterField(
            model_name='noticesettings',
            name='jam_content',
            field=models.TextField(help_text='\u5b9e\u65f6\u76d1\u63a7\u670d\u52a1\u5668\u5904\u7406\u72b6\u6001\uff0c\u5f53\u4e2d\u7ee7\u68c0\u6d4b\u6570\uff0b\u4e2d\u7ee7\u4f20\u8f93\u6570\uff0b\u7f51\u5173\u68c0\u6d4b\u6570\uff0b\u7f51\u5173\u53d1\u9001\u6570\u8d85\u8fc7\u9600\u503c\u65f6\uff0c\u53d1\u9001\u901a\u77e5,\u652f\u6301\u53d8\u91cf: {count}\u8868\u793a\u603b\u6570,{relay_check}\u8868\u793a\u4e2d\u7ee7\u68c0\u6d4b\u6570,{relay_dispatch}\u8868\u793a\u4e2d\u7ee7\u4f20\u8f93\u6570,{collect_check}\u8868\u793a\u7f51\u5173\u68c0\u6d4b\u6570,{collect_send}\u8868\u793a\u7f51\u5173\u53d1\u9001\u6570', null=True, verbose_name='\u670d\u52a1\u5668\u62e5\u5835\u901a\u77e5', blank=True),
        ),
    ]
