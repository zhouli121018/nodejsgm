# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0022_settings_max_size'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvalidSenderWhitelist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sender', models.CharField(help_text='\u65e0\u6548\u5730\u5740\u53d1\u4ef6\u4eba\u767d\u540d\u5355 \u5982\u679c\u53d1\u4ef6\u4eba\u5728\u767d\u540d\u5355\u4e2d\uff0c\u8df3\u8fc7\u4e2d\u7ee7\u65e0\u6548\u5730\u5740\u68c0\u6d4b', max_length=150, verbose_name='\u53d1\u4ef6\u4eba')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
    ]
