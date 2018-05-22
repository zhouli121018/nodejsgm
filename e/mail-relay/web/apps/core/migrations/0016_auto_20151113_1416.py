# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20151111_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mypermission',
            name='name',
            field=models.CharField(help_text='\u8bf7\u4f7f\u7528\u82f1\u6587\u540d\u79f0', unique=True, max_length=20, verbose_name='\u6743\u9650\u540d\u79f0'),
        ),
        migrations.AlterField(
            model_name='mypermission',
            name='url',
            field=models.CharField(max_length=150, null=True, verbose_name='\u76ee\u5f55url', blank=True),
        ),
    ]
