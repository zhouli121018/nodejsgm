# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='company',
            field=models.CharField(unique=True, max_length=50, verbose_name='\u516c\u53f8\u540d\u79f0'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='username',
            field=models.CharField(unique=True, max_length=50, verbose_name='\u5ba2\u6237\u5e10\u53f7'),
        ),
    ]
