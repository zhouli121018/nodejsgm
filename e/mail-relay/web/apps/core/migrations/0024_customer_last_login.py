# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_postfixstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='last_login',
            field=models.DateTimeField(null=True, verbose_name='\u6700\u540e\u767b\u5f55\u65f6\u95f4', blank=True),
        ),
    ]
