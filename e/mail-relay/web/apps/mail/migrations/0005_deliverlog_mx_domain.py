# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0004_auto_20150825_0945'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverlog',
            name='mx_domain',
            field=models.CharField(max_length=50, null=True, verbose_name='mx \u8bb0\u5f55', blank=True),
        ),
    ]
