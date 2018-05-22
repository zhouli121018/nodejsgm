# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collect', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='colcustomerdomain',
            name='domain',
            field=models.CharField(max_length=100, verbose_name='\u5ba2\u6237\u57df\u540d'),
        ),
        migrations.AlterField(
            model_name='colcustomerdomain',
            name='ip',
            field=models.GenericIPAddressField(verbose_name='\u57df\u540d\u5bf9\u5e94ip'),
        ),
    ]
