# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flag', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bigquotaflag',
            name='collect',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4ee3\u6536'),
        ),
        migrations.AddField(
            model_name='bigquotaflag',
            name='relay',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4e2d\u7ee7'),
        ),
        migrations.AddField(
            model_name='notexistflag',
            name='collect',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4ee3\u6536'),
        ),
        migrations.AddField(
            model_name='notexistflag',
            name='relay',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4e2d\u7ee7'),
        ),
        migrations.AddField(
            model_name='notretryflag',
            name='collect',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4ee3\u6536'),
        ),
        migrations.AddField(
            model_name='spamflag',
            name='collect',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4ee3\u6536'),
        ),
        migrations.AddField(
            model_name='spfflag',
            name='collect',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4ee3\u6536'),
        ),
    ]
