# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0079_customersetting_interval_spamrpt'),
        ('mail', '0111_spfchecklist_direct_reject'),
    ]

    operations = [
        migrations.AddField(
            model_name='relaysenderwhitelist',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to='core.Customer', null=True),
        ),
        migrations.AddField(
            model_name='relaysenderwhitelist',
            name='note',
            field=models.CharField(help_text='\u5907\u6ce8', max_length=200, null=True, verbose_name='\u5907\u6ce8', blank=True),
        ),
    ]
