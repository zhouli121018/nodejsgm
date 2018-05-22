# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0016_auto_20151110_0951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invalidmail',
            name='mail',
            field=models.CharField(help_text='\u65e0\u6548\u90ae\u4ef6\u5730\u5740', unique=True, max_length=150, verbose_name='\u90ae\u4ef6\u5730\u5740', db_index=True),
        ),
    ]
