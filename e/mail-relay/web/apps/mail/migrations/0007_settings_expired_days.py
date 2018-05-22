# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0006_auto_20150827_1505'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='expired_days',
            field=models.IntegerField(default=15, help_text='\u5355\u4f4d\uff1a\u5929\u6570\uff0c\u5982\u679c\u5ba2\u6237\u670d\u52a1\u5230\u671f\uff0c\u53ef\u5ef6\u957f\u53d1\u9001\u76f8\u5e94\u5929\u6570', verbose_name='\u5ba2\u6237\u8fc7\u671f\u5ef6\u957f\u5929\u6570'),
        ),
    ]
