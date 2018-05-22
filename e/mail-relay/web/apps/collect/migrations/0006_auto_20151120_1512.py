# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collect', '0005_auto_20151118_1721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='colcustomerdomain',
            name='ip',
            field=models.CharField(max_length=100, verbose_name='\u8f6c\u53d1\u5730\u5740'),
        ),
    ]
