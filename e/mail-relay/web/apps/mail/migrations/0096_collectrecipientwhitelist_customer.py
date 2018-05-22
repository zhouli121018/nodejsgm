# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0057_auto_20170517_1057'),
        ('mail', '0095_auto_20170517_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectrecipientwhitelist',
            name='customer',
            field=models.ForeignKey(blank=True, to='core.Customer', null=True),
        ),
    ]
