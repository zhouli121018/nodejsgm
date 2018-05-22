# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0099_auto_20170522_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkstatistics',
            name='high_sender_all',
            field=models.IntegerField(default=0, verbose_name='\u9ad8\u5371\u53d1\u4ef6\u4eba\u5168\u90e8'),
        ),
        migrations.AddField(
            model_name='checkstatistics',
            name='high_sender_pass',
            field=models.IntegerField(default=0, verbose_name='\u9ad8\u5371\u53d1\u4ef6\u4eba\u901a\u8fc7'),
        ),
    ]
