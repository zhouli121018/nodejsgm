# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collect_mail', '0011_auto_20160810_1018'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistics',
            name='error_type_8',
            field=models.IntegerField(default=0, verbose_name='\u53d1\u9001\u8d85\u65f6'),
        ),
    ]
