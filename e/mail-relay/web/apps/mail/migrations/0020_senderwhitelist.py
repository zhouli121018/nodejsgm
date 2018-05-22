# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collect', '0003_colcustomersetting_check_sender'),
        ('mail', '0019_auto_20151113_1727'),
    ]

    operations = [
        migrations.CreateModel(
            name='SenderWhitelist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sender', models.CharField(help_text='\u53d1\u4ef6\u4eba\u767d\u540d\u5355 \u5982\u679c\u53d1\u4ef6\u4eba\u5728\u767d\u540d\u5355\u4e2d\uff0c\u8df3\u8fc7\u540e\u9762\u6240\u6709\u7684\u7f51\u5173\u68c0\u6d4b', max_length=150, verbose_name='\u53d1\u4ef6\u4eba')),
                ('is_global', models.BooleanField(default=False, help_text='\u5168\u5c40\u767d\uff0c\u662f\u5bf9\u6240\u6709\u5ba2\u6237\u751f\u6548\u3002\u5ba2\u6237\u767d\uff0c\u4ec5\u4ec5\u5bf9\u8fd9\u4e2a\u5ba2\u6237\u751f\u6548', verbose_name='\u662f\u5426\u4e3a\u5168\u5c40\u53d8\u91cf')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='collect.ColCustomer', null=True)),
            ],
        ),
    ]
