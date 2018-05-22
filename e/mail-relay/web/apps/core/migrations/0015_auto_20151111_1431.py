# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20151111_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mypermission',
            name='permission',
            field=models.ForeignKey(blank=True, to='auth.Permission', null=True),
        ),
    ]
