# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_mypermission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mypermission',
            name='parent',
            field=models.ForeignKey(related_name='children', blank=True, to='core.MyPermission', null=True),
        ),
    ]
