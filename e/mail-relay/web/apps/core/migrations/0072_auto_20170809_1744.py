# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0071_customer_is_webmail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='contact',
            field=models.CharField(max_length=100, null=True, verbose_name='\u8054\u7cfb\u4eba', blank=True),
        ),
    ]
