# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0063_auto_20170527_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='customersetting',
            name='c_bounce',
            field=models.BooleanField(default=False, verbose_name='\u7f51\u5173:\u5f00\u542f\u9000\u4fe1'),
        ),
    ]
