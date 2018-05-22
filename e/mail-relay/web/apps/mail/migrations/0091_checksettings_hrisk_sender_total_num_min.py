# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0090_auto_20160902_1701'),
    ]

    operations = [
        migrations.AddField(
            model_name='checksettings',
            name='hrisk_sender_total_num_min',
            field=models.IntegerField(default=10, help_text='\u5355\u4f4d:\u4e2a\u6570, \u90ae\u4ef6\u603b\u6570\u8d85\u8fc7\u8be5\u6700\u5c0f\u9600\u503c\uff0c\u4e14\u62d2\u7edd+\u53d1\u9001\u5931\u8d25\u7684\u90ae\u4ef6\u5360\u90ae\u4ef6\u603b\u6570\u7684\u6bd4\u4f8b\uff0c \u8fbe\u5230\u5219\u5728\u67d0\u6bb5\u65f6\u95f4\u5185\u62e6\u622a\u5176\u6240\u6709\u90ae\u4ef6\uff0c\u5e76\u653e\u5165\u201c\u9ad8\u5371\u53d1\u4ef6\u4eba\u201d\u8fdb\u884c\u4eba\u5de5\u5ba1\u6838', verbose_name='\u9ad8\u5371\u53d1\u4ef6\u4eba\u90ae\u4ef6\u603b\u6570\u6700\u5c0f\u9600\u503c'),
        ),
    ]
