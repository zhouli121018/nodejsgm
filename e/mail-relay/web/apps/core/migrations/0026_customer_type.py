# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20151210_1452'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='type',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='\u5ba2\u6237\u7c7b\u578b', choices=[(b'', b'--'), (b'relay', '\u4e2d\u7ee7'), (b'collect', '\u7f51\u5173'), (b'all', '\u5168\u90e8(\u4e2d\u7ee7/\u7f51\u5173)')]),
        ),
    ]
