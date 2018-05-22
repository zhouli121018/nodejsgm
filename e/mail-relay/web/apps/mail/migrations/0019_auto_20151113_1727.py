# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0018_auto_20151113_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulkcustomer',
            name='date',
            field=models.DateField(),
        ),
    ]
