# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0031_recipientwhitelist'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='sync_max_size',
            field=models.IntegerField(default=800, help_text='\u5355\u4f4d\uff1aKB\uff0c\u5982\u679c\u90ae\u4ef6\u5927\u5c0f\u8d85\u8fc7\u8be5\u9600\u503c\uff0c\u5219\u8be5\u90ae\u4ef6\u5185\u5bb9\u4e0d\u4f1a\u540c\u6b65\u5230\u5176\u4ed6\u670d\u52a1\u5668', verbose_name='\u90ae\u4ef6\u540c\u6b65\u6700\u5927\u9600\u503c'),
        ),
    ]
