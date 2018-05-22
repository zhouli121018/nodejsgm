# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0003_auto_20150819_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='back_days',
            field=models.IntegerField(default=30, help_text='\u5355\u4f4d\uff1a\u5929\u6570\uff0c\u8d85\u8fc7\u8be5\u5929\u6570\u7684\u539f\u59cb\u90ae\u4ef6\u5c06\u4f1a\u88ab\u81ea\u52a8\u6e05\u9664', verbose_name='\u90ae\u4ef6\u5907\u4efd\u65e5\u671f'),
        ),
    ]
