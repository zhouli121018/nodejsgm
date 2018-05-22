# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('localized_mail', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='localizedmail',
            name='mail_id',
            field=models.CharField(max_length=20, null=True, verbose_name='\u5ba2\u6237\u90ae\u4ef6ID', blank=True),
        ),
    ]
