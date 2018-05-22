# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0072_auto_20170809_1744'),
    ]

    operations = [
        migrations.AddField(
            model_name='customersetting',
            name='check_format',
            field=models.BooleanField(default=True, verbose_name='\u7f51\u5173\u8fc7\u6ee4:\u53d1\u4ef6\u4eba\u683c\u5f0f\u68c0\u6d4b'),
        ),
    ]
