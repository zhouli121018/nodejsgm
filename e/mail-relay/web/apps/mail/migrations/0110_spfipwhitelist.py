# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mail', '0109_auto_20171130_1047'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpfIpWhitelist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u5982\u679c\u53d1\u4ef6\u4eba\u6765\u6e90IP\u5728\u767d\u540d\u5355\u4e2d\uff0c\u5219\u4e0d\u8fdb\u884cSPF\u68c0\u6d4b', unique=True, max_length=150, verbose_name='IP')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('operate_time', models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True)),
                ('creater', models.ForeignKey(related_name='spfip_creater', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('operater', models.ForeignKey(related_name='spfip_operater', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': '\u7f51\u5173SPF ip\u767d\u540d\u5355',
            },
        ),
    ]
