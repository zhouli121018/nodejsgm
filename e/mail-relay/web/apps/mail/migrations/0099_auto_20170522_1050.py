# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0098_auto_20170522_0940'),
    ]

    operations = [
        migrations.AddField(
            model_name='checksettings',
            name='hrisk_diff_sender_count',
            field=models.IntegerField(default=3, help_text='\u4e00\u5929\u5185 \u540c\u4e00\u53d1\u4ef6\u4eba\u540d\u79f0\u4e0d\u540c\u503c\u8d85\u8fc7N\u6b21\uff0c \u5219\u5728\u4ee5\u540e\u7684M\u65f6\u95f4\u5185\u62e6\u622a\u5176\u6240\u6709\u90ae\u4ef6\uff0c\u5e76\u653e\u5165\u201c\u9ad8\u5371\u53d1\u4ef6\u4eba\u201d\u8fdb\u884c\u4eba\u5de5\u5ba1\u6838', verbose_name='\u540d\u79f0\u4e0d\u540c\u7684\u9ad8\u5371\u53d1\u4ef6\u4eba(\u4e0d\u540c\u6b21\u6570)'),
        ),
        migrations.AddField(
            model_name='checksettings',
            name='hrisk_diff_sender_time',
            field=models.IntegerField(default=600, help_text='\u5355\u4f4d:\u5206\u949f, \u4e00\u5929\u5185 \u540c\u4e00\u53d1\u4ef6\u4eba\u540d\u79f0\u4e0d\u540c\u503c\u8d85\u8fc7N\u6b21\uff0c \u5219\u5728\u4ee5\u540e\u7684M\u65f6\u95f4\u5185\u62e6\u622a\u5176\u6240\u6709\u90ae\u4ef6\uff0c\u5e76\u653e\u5165\u201c\u9ad8\u5371\u53d1\u4ef6\u4eba\u201d\u8fdb\u884c\u4eba\u5de5\u5ba1\u6838', verbose_name='\u540d\u79f0\u4e0d\u540c\u7684\u9ad8\u5371\u53d1\u4ef6\u4eba(\u62e6\u622a\u65f6\u95f4)'),
        ),
    ]
