# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('flag', '0004_auto_20160127_1422'),
    ]

    operations = [
        migrations.CreateModel(
            name='GreyListFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u7070\u540d\u5355\u6807\u5fd7, \u53d1\u9001\u90ae\u4ef6\u8fd4\u56de\u4fe1\u606f\u4e2d\u5305\u542b\u6b64\u5185\u5bb9, \u5219\u8ba4\u4e3a\u662f\u7070\u540d\u5355\u90ae\u4ef6', max_length=50, verbose_name='\u7070\u540d\u5355\u6807\u5fd7')),
                ('relay', models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4e2d\u7ee7')),
                ('collect', models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4ee3\u6536')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('operate_time', models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True)),
                ('creater', models.ForeignKey(related_name='greylist_creater', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('operater', models.ForeignKey(related_name='greylist_operater', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
