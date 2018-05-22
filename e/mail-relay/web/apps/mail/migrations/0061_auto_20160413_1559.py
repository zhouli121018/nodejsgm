# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0060_auto_20160408_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='senderwhitelist',
            name='customer',
            field=models.ForeignKey(blank=True, to='core.Customer', null=True),
        ),
    ]
