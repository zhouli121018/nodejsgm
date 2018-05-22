# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0089_checksettings_esets_max_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='checksettings',
            name='hrisk_sender_check_time',
            field=models.IntegerField(default=60, help_text='\u5355\u4f4d:\u5206\u949f, \u5355\u4f4d\u65f6\u95f4\u5185\uff0c\u62d2\u7edd+\u53d1\u9001\u5931\u8d25\u7684\u90ae\u4ef6\u5360\u90ae\u4ef6\u603b\u6570\u7684\u6bd4\u4f8b\u8fbe\u5230\u4e00\u5b9a\u6bd4\u4f8b\uff0c\u5219\u5728\u67d0\u6bb5\u65f6\u95f4\u5185\u62e6\u622a\u5176\u6240\u6709\u90ae\u4ef6\uff0c\u5e76\u653e\u5165\u201c\u9ad8\u5371\u53d1\u4ef6\u4eba\u201d\u8fdb\u884c\u4eba\u5de5\u5ba1\u6838', verbose_name='\u9ad8\u5371\u53d1\u4ef6\u4eba\u68c0\u6d4b\u65f6\u95f4'),
        ),
        migrations.AddField(
            model_name='checksettings',
            name='hrisk_sender_scale',
            field=models.IntegerField(default=50, help_text='\u5355\u4f4d:%, \u62d2\u7edd+\u53d1\u9001\u5931\u8d25\u7684\u90ae\u4ef6\u5360\u90ae\u4ef6\u603b\u6570\u7684\u6bd4\u4f8b\uff0c\u8fbe\u5230\u5219\u5728\u67d0\u6bb5\u65f6\u95f4\u5185\u62e6\u622a\u5176\u6240\u6709\u90ae\u4ef6\uff0c\u5e76\u653e\u5165\u201c\u9ad8\u5371\u53d1\u4ef6\u4eba\u201d\u8fdb\u884c\u4eba\u5de5\u5ba1\u6838', verbose_name='\u9ad8\u5371\u53d1\u4ef6\u4eba\u9ad8\u5371\u90ae\u4ef6\u6570\u5360\u6bd4'),
        ),
        migrations.AddField(
            model_name='checksettings',
            name='hrisk_sender_time',
            field=models.IntegerField(default=60, help_text='\u5355\u4f4d:\u5206\u949f, \u53d1\u4ef6\u4eba\u5728\u6b64\u6bb5\u65f6\u95f4\u5185\u7684\u6240\u6709\u90ae\u4ef6\u88ab\u62e6\u622a\uff0c\u5e76\u653e\u5165\u201c\u9ad8\u5371\u53d1\u4ef6\u4eba\u201d\u8fdb\u884c\u4eba\u5de5\u5ba1\u6838', verbose_name='\u9ad8\u5371\u53d1\u4ef6\u4eba\u62e6\u622a\u65f6\u95f4'),
        ),
    ]
