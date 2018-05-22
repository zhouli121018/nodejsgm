# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20150902_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='support_id',
            field=models.CharField(max_length=50, null=True, verbose_name='\u5ba2\u6237\u670d\u52a1\u5e73\u53f0\u5bf9\u63a5\u5b57\u6bb5', blank=True),
        ),
    ]
