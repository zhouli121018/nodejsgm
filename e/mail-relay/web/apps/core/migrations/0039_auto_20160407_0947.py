# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_auto_20160406_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='colcustomerdomain',
            name='is_ssl',
            field=models.BooleanField(default=False, help_text='\u662f\u5426ssl\u52a0\u5bc6\u8f6c\u53d1\uff0c\u9ed8\u8ba4False', verbose_name='\u662f\u5426\u52a0\u5bc6'),
        ),
        migrations.AddField(
            model_name='colcustomerdomain',
            name='port',
            field=models.IntegerField(default=25, help_text='\u8f6c\u53d1\u7aef\u53e3,\u9ed8\u8ba425', verbose_name='\u8f6c\u53d1\u7aef\u53e3'),
        ),
    ]
