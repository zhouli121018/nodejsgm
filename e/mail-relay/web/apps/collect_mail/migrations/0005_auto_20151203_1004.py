# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collect_mail', '0004_auto_20151102_1520'),
    ]

    operations = [
        # migrations.AlterField(
        #     model_name='statistics',
        #     name='customer',
        #     field=models.ForeignKey(related_name='collect_statistics', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Customer', null=True),
        # ),
    ]
