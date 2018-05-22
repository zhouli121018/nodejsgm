# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0011_auto_20151022_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='keywordblacklist',
            name='collect',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4ee3\u6536'),
        ),
        migrations.AddField(
            model_name='keywordblacklist',
            name='relay',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4e2d\u7ee7'),
        ),
        migrations.AddField(
            model_name='senderblacklist',
            name='collect',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4ee3\u6536'),
        ),
        migrations.AddField(
            model_name='senderblacklist',
            name='relay',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4e2d\u7ee7'),
        ),
        migrations.AddField(
            model_name='subjectkeywordblacklist',
            name='collect',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4ee3\u6536'),
        ),
        migrations.AddField(
            model_name='subjectkeywordblacklist',
            name='relay',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4e2d\u7ee7'),
        ),
    ]
