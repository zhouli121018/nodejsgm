# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0100_auto_20170523_1439'),
    ]

    operations = [
        migrations.AddField(
            model_name='noticesettings',
            name='sender_warning_content',
            field=models.TextField(help_text='\u4e2d\u7ee7\u90ae\u4ef6\u5ba1\u6838\u9875\u9762\uff0c\u589e\u52a0\u6309\u94ae\uff1a\u90ae\u4ef6\u63d0\u9192\u53d1\u4ef6\u4eba\uff08\u53d1\u9001\u4e00\u5c01\u90ae\u4ef6\u63d0\u9192\u7528\u6237\u5728\u7fa4\u53d1\u5783\u573e\u75c5\u6bd2\u90ae\u4ef6, {mail_from}\u8868\u793a\u90ae\u4ef6\u53d1\u4ef6\u4eba', null=True, verbose_name='\u53d1\u4ef6\u4eba\u63d0\u9192', blank=True),
        ),
    ]
