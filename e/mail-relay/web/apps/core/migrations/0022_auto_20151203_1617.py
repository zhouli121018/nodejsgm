# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20151203_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersetting',
            name='check_rbl',
            field=models.BooleanField(default=False, verbose_name='\u7f51\u5173\u8fc7\u6ee4:rbl'),
        ),
        migrations.AlterField(
            model_name='customersetting',
            name='check_spf',
            field=models.BooleanField(default=False, verbose_name='\u7f51\u5173\u8fc7\u6ee4:spf'),
        ),
    ]
