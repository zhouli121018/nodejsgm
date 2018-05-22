# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20151203_1146'),
    ]

    operations = [
        migrations.AddField(
            model_name='customersetting',
            name='check_rbl',
            field=models.BooleanField(default=True, verbose_name='\u7f51\u5173\u8fc7\u6ee4:rbl'),
        ),
        migrations.AddField(
            model_name='customersetting',
            name='check_spf',
            field=models.BooleanField(default=True, verbose_name='\u7f51\u5173\u8fc7\u6ee4:spf'),
        ),
        migrations.AlterField(
            model_name='customersetting',
            name='bounce',
            field=models.BooleanField(default=False, verbose_name='\u4e2d\u7ee7:\u5f00\u542f\u9000\u4fe1'),
        ),
    ]
