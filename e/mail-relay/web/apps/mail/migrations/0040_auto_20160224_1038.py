# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0039_auto_20160203_1417'),
    ]

    operations = [
        migrations.AddField(
            model_name='checksettings',
            name='c_night_spam_score_max',
            field=models.FloatField(default=4.0, help_text='\u665a\u4e0a(19:00--07:00)\u5982\u679cspam\u68c0\u6d4b\u5206\u6570\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u88ab\u8ba4\u4e3a\u662f\u5783\u573e\u90ae\u4ef6, \u9ed8\u8ba4\u4e3a5.0', verbose_name='\u7f51\u5173spam\u68c0\u6d4b\u5206\u6570\u9600\u503c(\u665a\u4e0a)'),
        ),
        migrations.AddField(
            model_name='checksettings',
            name='c_spam_score_max',
            field=models.FloatField(default=5.0, help_text='\u767d\u5929(07:00--19:00)\u5982\u679cspam\u68c0\u6d4b\u5206\u6570\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u88ab\u8ba4\u4e3a\u662f\u5783\u573e\u90ae\u4ef6, \u9ed8\u8ba4\u4e3a5.0', verbose_name='\u7f51\u5173spam\u68c0\u6d4b\u5206\u6570\u9600\u503c(\u767d\u5929)'),
        ),
        migrations.AlterField(
            model_name='checksettings',
            name='night_spam_score_max',
            field=models.FloatField(default=4.0, help_text='\u665a\u4e0a(19:00--07:00)\u5982\u679cspam\u68c0\u6d4b\u5206\u6570\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u88ab\u8ba4\u4e3a\u662f\u5783\u573e\u90ae\u4ef6, \u9ed8\u8ba4\u4e3a5.0', verbose_name='\u4e2d\u7ee7spam\u68c0\u6d4b\u5206\u6570\u9600\u503c(\u665a\u4e0a)'),
        ),
        migrations.AlterField(
            model_name='checksettings',
            name='spam_score_max',
            field=models.FloatField(default=5.0, help_text='\u767d\u5929(07:00--19:00)\u5982\u679cspam\u68c0\u6d4b\u5206\u6570\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u88ab\u8ba4\u4e3a\u662f\u5783\u573e\u90ae\u4ef6, \u9ed8\u8ba4\u4e3a5.0', verbose_name='\u4e2d\u7ee7spam\u68c0\u6d4b\u5206\u6570\u9600\u503c(\u767d\u5929)'),
        ),
    ]
