# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0045_auto_20160316_1436'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='keywordblacklist',
            options={'ordering': ('order',)},
        ),
        migrations.AddField(
            model_name='keywordblacklist',
            name='order',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
    ]
