# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mail', '0085_auto_20160809_1125'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelaySenderWhitelist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sender', models.CharField(help_text='\u5982\u679c\u53d1\u4ef6\u4eba\u5728\u4e2d\u7ee7\u53d1\u4ef6\u4eba\u767d\u540d\u5355\u4e2d\uff0c\u4e0d\u8fdb\u884c\u7fa4\u53d1\u9891\u7387\u9650\u5236\uff0c\u4e0d\u8fdb\u884c\u4efb\u4f55\u68c0\u6d4b\u3002\u4e0d\u652f\u6301\u6b63\u5219\u3002', unique=True, max_length=150, verbose_name='\u53d1\u4ef6\u4eba')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('operate_time', models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True)),
                ('creater', models.ForeignKey(related_name='creater201', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('operater', models.ForeignKey(related_name='operater201', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
