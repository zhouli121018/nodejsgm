# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collect', '0004_colcustomersetting_check_ctasd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='colcustomersetting',
            name='check_ctasd',
            field=models.BooleanField(default=True, verbose_name='cyber\u8fc7\u6ee4'),
        ),
    ]
