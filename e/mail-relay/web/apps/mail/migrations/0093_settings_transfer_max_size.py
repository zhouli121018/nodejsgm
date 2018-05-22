# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0092_statistics_error_type_8'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='transfer_max_size',
            field=models.IntegerField(default=5, help_text='\u5355\u4f4d\uff1aM\uff0c\u90ae\u4ef6\u5927\u5c0f\u8d85\u8fc7\u8be5\u9600\u503c\uff0c\u5219\u8be5\u90ae\u4ef6\u53d1\u9001\u65f6\u81ea\u52a8\u8f6c\u7f51\u7edc\u9644\u4ef6', verbose_name='\u81ea\u52a8\u8f6c\u7f51\u7edc\u9644\u4ef6\u6700\u5927\u9600\u503c'),
        ),
    ]
