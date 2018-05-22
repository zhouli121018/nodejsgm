# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0075_auto_20171130_1004'),
    ]

    operations = [
        migrations.AddField(
            model_name='colcustomerdomain',
            name='priority',
            field=models.SmallIntegerField(default=0, verbose_name='\u4f18\u5148\u7ea7'),
        ),
    ]
