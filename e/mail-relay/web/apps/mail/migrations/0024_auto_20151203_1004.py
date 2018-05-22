# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0023_invalidsenderwhitelist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='senderwhitelist',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Customer', null=True),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='customer',
            field=models.ForeignKey(related_name='relay_statistics', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Customer', null=True),
        ),
    ]
