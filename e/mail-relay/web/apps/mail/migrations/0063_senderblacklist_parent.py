# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0062_auto_20160425_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='senderblacklist',
            name='parent',
            field=models.ForeignKey(related_name='children', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='mail.SenderBlacklist', null=True),
        ),
    ]
