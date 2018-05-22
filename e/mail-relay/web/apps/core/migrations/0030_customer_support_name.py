# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20151223_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='support_name',
            field=models.CharField(max_length=50, null=True, verbose_name='\u5ba2\u6237\u652f\u6301\u540d\u79f0', blank=True),
        ),
    ]
