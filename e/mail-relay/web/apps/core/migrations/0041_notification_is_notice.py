# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_auto_20160408_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='is_notice',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u53d1\u7ad9\u5185\u901a\u77e5'),
        ),
    ]
