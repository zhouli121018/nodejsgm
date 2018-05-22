# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0093_settings_transfer_max_size'),
    ]

    operations = [
        migrations.CreateModel(
            name='EdmCheckSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='\u53d1\u5783\u573e\u68c0\u6d4b\u5f15\u64ce\u540d\u79f0\uff0c\u5982\uff1aQQ\u53cd\u5783\u573e\u68c0\u6d4b\u5f15\u64ce, \u67d0\u67d0\u53cd\u5783\u573e\u68c0\u6d4b\u5f15\u64ce...', max_length=50, verbose_name='\u540d\u79f0')),
                ('smtp_server', models.CharField(help_text='SMTP\u670d\u52a1\u5546\u5730\u5740, \u5982\uff1asmtp.qq.com', max_length=100, verbose_name='SMTP\u670d\u52a1\u5546')),
                ('smtp_port', models.IntegerField(default=25, help_text='SMTP\u670d\u52a1\u5546\u7aef\u53e3', verbose_name='SMTP\u7aef\u53e3')),
                ('account', models.CharField(help_text='SMTP\u8d26\u53f7', max_length=100, verbose_name='SMTP\u8d26\u53f7')),
                ('password', models.CharField(help_text='SMTP\u5bc6\u7801', max_length=100, verbose_name='SMTP\u5bc6\u7801')),
                ('receiver', models.CharField(help_text='\n        SMTP\u8d26\u53f7\u53d1\u9001\u68c0\u6d4b\u5c31\u662f\u7528\u4e00\u4e2a\u6216\u591a\u4e2asmtp\u8d26\u53f7\u53d1\u9001\u6d4b\u8bd5\uff0c\u5982\u679c\u8fd4\u56de\u4fe1\u606f\u91cc\u6709\u5783\u573e\u90ae\u4ef6\u6807\u5fd7\uff0c\u5219\u6a21\u677f\u4e3a\u7ea2\u8272\n        \u68c0\u6d4b\u5783\u573e\u7684SMTP\u8d26\u53f7\u53ef\u80fd\u4f1a\u6709\u591a\u4e2a\uff0c\u7ba1\u7406\u5458\u540e\u53f0\u8bbe\u7f6e\u683c\u5f0f\u8303\u4f8b\uff1a\n        QQ\u53cd\u5783\u573e\u68c0\u6d4b\u5f15\u64ce smtp.qq.com 56656565@qq.com password \u6536\u4ef6\u4eba\u90ae\u7bb1\n        \u67d0\u67d0\u53cd\u5783\u573e\u5f15\u64ce smtp.aaa.com  adfb@ss.com password \u6536\u4ef6\u4eba\u90ae\u7bb1\n        \u7cfb\u7edf\u8c03\u7528\u4e0a\u8ff0SMTP\u8d26\u53f7\u6295\u9012\u90ae\u4ef6\uff0c\u5982\u679c\u51fa\u73b0 \u5783\u573e\u90ae\u4ef6\u6807\u5fd7\uff0c\u5219\u8fd4\u56de\u7ea2\u8272\u5e76\u63d0\u793a \u67d0\u67d0\u53cd\u5783\u573e\u5f15\u64ce \u68c0\u6d4b\u4e3a\u5783\u573e\u90ae\u4ef6\n    ', max_length=100, verbose_name='\u6536\u4ef6\u4eba\u90ae\u7bb1')),
            ],
        ),
    ]
