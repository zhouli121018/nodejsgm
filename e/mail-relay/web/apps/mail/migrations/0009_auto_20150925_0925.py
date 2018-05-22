# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0008_validmailsuffix'),
    ]

    operations = [
        migrations.AddField(
            model_name='checksettings',
            name='bulk_sender_max',
            field=models.IntegerField(default=10, help_text='\u5355\u4e2a\u53d1\u4ef6\u4eba\u5728\u76d1\u6d4b\u65f6\u95f4\u5185\u5141\u8bb8\u53d1\u7684\u90ae\u4ef6\u5c01\u6570\uff0c\u8d85\u8fc7\u7684\u63a5\u6536\u5e76\u4e22\u5f03\uff0c\u5c06\u90ae\u4ef6\u6570\u8ba1\u5165\u7fa4\u53d1', verbose_name='\u7fa4\u53d1\u5355\u53d1\u4ef6\u4eba\u53d1\u9001\u9600\u503c'),
        ),
        migrations.AddField(
            model_name='checksettings',
            name='bulk_sender_time',
            field=models.IntegerField(default=10, help_text='\u5355\u4f4d\uff1a\u5206\u949f\uff0c\u7fa4\u53d1\u76d1\u6d4b\u5355\u4e2a\u53d1\u4ef6\u4eba\u7684\u65f6\u95f4', verbose_name='\u7fa4\u53d1\u5355\u4e2a\u53d1\u4ef6\u4eba\u76d1\u6d4b\u65f6\u95f4'),
        ),
    ]
