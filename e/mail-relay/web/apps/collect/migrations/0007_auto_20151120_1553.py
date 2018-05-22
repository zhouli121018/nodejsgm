# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collect', '0006_auto_20151120_1512'),
    ]

    operations = [
        migrations.RenameField(
            model_name='colcustomerdomain',
            old_name='ip',
            new_name='forward_address',
        ),
    ]
