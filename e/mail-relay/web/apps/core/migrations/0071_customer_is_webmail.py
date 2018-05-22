# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0070_auto_20170731_1031'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='is_webmail',
            field=models.BooleanField(default=0, verbose_name='\u662f\u5426\u4e3a\u90ae\u4ef6\u7cfb\u7edf'),
        ),
    ]
