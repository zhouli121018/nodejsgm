# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0021_checksettings_ctasd_max_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='max_size',
            field=models.IntegerField(default=0, help_text='\u5355\u4f4d\uff1aKB\uff0c\u5982\u679c\u90ae\u4ef6\u5927\u5c0f\u8d85\u8fc7\u8be5\u9600\u503c\uff0c\u5219\u8be5\u90ae\u4ef6\u4e0d\u52a0\u5165\u5f52\u6863\u90ae\u7bb1\u5199\u53d1\u6210\u529f\u540e\u76f4\u63a5\u5220\u9664\uff0c0\u8868\u793a\u8be5\u8bbe\u7f6e\u65e0\u6548', verbose_name='\u5927\u90ae\u4ef6\u9600\u503c'),
        ),
    ]
