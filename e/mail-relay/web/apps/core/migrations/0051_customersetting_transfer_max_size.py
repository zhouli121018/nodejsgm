# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0050_customersetting_can_view_mail'),
    ]

    operations = [
        migrations.AddField(
            model_name='customersetting',
            name='transfer_max_size',
            field=models.IntegerField(default=0, help_text='\u5355\u4f4d\uff1aM\uff0c\u90ae\u4ef6\u5927\u5c0f\u8d85\u8fc7\u8be5\u9600\u503c\uff0c\u5219\u8be5\u90ae\u4ef6\u53d1\u9001\u65f6\u81ea\u52a8\u8f6c\u7f51\u7edc\u9644\u4ef6, \u9ed8\u8ba4\u503c\uff10, \u8868\u793a\u7528\u7cfb\u7edf\u9ed8\u8ba4\u8bbe\u7f6e\u503c', verbose_name='\u4e2d\u7ee7\uff1a\u81ea\u52a8\u8f6c\u7f51\u7edc\u9644\u4ef6\u6700\u5927\u9600\u503c'),
        ),
    ]
