# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flag', '0002_auto_20151102_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='notretryflag',
            name='relay',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4e2d\u7ee7'),
        ),
        migrations.AddField(
            model_name='spamflag',
            name='relay',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4e2d\u7ee7'),
        ),
        migrations.AddField(
            model_name='spfflag',
            name='relay',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4e2d\u7ee7'),
        ),
    ]
