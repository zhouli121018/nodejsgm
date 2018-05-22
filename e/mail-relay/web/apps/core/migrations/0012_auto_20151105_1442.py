# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_customersetting'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersetting',
            name='bounce',
            field=models.BooleanField(default=True, verbose_name='\u5f00\u542f\u9000\u4fe1'),
        ),
    ]
