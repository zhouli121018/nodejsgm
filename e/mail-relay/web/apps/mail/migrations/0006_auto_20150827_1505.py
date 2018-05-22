# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0005_deliverlog_mx_domain'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliverlog',
            name='mx_domain',
        ),
        migrations.AddField(
            model_name='deliverlog',
            name='mx_record',
            field=models.CharField(max_length=200, null=True, verbose_name='mx \u8bb0\u5f55', blank=True),
        ),
    ]
