# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0027_auto_20151222_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulkcustomer',
            name='note',
            field=models.CharField(help_text='\u5907\u6ce8', max_length=200, null=True, verbose_name='\u5907\u6ce8', blank=True),
        ),
        migrations.AddField(
            model_name='spferror',
            name='note',
            field=models.CharField(help_text='\u5907\u6ce8', max_length=200, null=True, verbose_name='\u5907\u6ce8', blank=True),
        ),
    ]
