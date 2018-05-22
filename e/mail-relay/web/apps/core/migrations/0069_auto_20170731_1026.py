# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0068_corelog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clusterip',
            name='ip',
            field=models.CharField(unique=True, max_length=100, verbose_name='IP\u5730\u5740'),
        ),
    ]
