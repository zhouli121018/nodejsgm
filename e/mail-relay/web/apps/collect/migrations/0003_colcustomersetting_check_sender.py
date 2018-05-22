# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collect', '0002_auto_20151029_1403'),
    ]

    operations = [
        migrations.AddField(
            model_name='colcustomersetting',
            name='check_sender',
            field=models.BooleanField(default=True, verbose_name='\u53d1\u4ef6\u4eba\u9ed1\u540d\u5355\u8fc7\u6ee4'),
        ),
    ]
