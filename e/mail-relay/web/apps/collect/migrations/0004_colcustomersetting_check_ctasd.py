# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collect', '0003_colcustomersetting_check_sender'),
    ]

    operations = [
        migrations.AddField(
            model_name='colcustomersetting',
            name='check_ctasd',
            field=models.BooleanField(default=True, verbose_name='ctasd\u8fc7\u6ee4'),
        ),
    ]
