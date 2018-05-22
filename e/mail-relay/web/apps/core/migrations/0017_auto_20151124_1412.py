# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20151113_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerip',
            name='ip',
            field=models.CharField(max_length=20, verbose_name='\u5ba2\u6237\u56fa\u5b9aip'),
        ),
    ]
