# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_auto_20160407_0947'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='is_notice',
        ),
        migrations.AlterField(
            model_name='colcustomerdomain',
            name='is_ssl',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u52a0\u5bc6'),
        ),
        migrations.AlterField(
            model_name='colcustomerdomain',
            name='port',
            field=models.IntegerField(default=25, verbose_name='\u8f6c\u53d1\u7aef\u53e3'),
        ),
    ]
