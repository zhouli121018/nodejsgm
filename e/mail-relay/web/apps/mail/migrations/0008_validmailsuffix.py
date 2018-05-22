# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0007_settings_expired_days'),
    ]

    operations = [
        migrations.CreateModel(
            name='ValidMailSuffix',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u6709\u6548\u7684\u90ae\u4ef6\u540e\u7f00\u540d', max_length=50, verbose_name='\u90ae\u4ef6\u540e\u7f00\u540d')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
    ]
