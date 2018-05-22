# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20151124_1412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersetting',
            name='bounce',
            field=models.BooleanField(default=False, verbose_name='\u5f00\u542f\u9000\u4fe1'),
        ),
    ]
