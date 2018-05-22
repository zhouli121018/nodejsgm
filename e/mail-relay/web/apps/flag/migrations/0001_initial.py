# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BigQuotaFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u8d85\u5927/\u6ee1\u7684\u90ae\u4ef6\u6807\u5fd7, \u53d1\u9001\u90ae\u4ef6\u8fd4\u56de\u4fe1\u606f\u4e2d\u5305\u542b\u6b64\u5185\u5bb9, \u5219\u8ba4\u4e3a\u662f\u8d85\u5927/\u6ee1\u7684\u90ae\u4ef6', max_length=50, verbose_name='\u8d85\u5927/\u6ee1\u7684\u90ae\u4ef6\u6807\u5fd7')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
        migrations.CreateModel(
            name='HighRiskFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u9ad8\u5371\u9644\u4ef6\u6807\u5fd7, \u5bf9\u9644\u4ef6\u8fdb\u884c\u76d1\u63a7\uff0c\u9644\u4ef6\u7684\u7c7b\u578b\u53ef\u5b9a\u4e49\uff0c\u6bd4\u5982js\u3001vbs\u7b49\u3002\u542b\u6709\u6b64\u7c7b\u9644\u4ef6\u7684\u90ae\u4ef6\u653e\u5165\u9ad8\u5371\u90ae\u4ef6\u5ba1\u6838\u3002', max_length=50, verbose_name='\u9ad8\u5371\u9644\u4ef6\u6807\u5fd7')),
                ('relay', models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4e2d\u7ee7')),
                ('collect', models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4ee3\u6536')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
        migrations.CreateModel(
            name='NotExistFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u90ae\u7bb1\u4e0d\u5b58\u5728\u6807\u5fd7, \u53d1\u9001\u90ae\u4ef6\u8fd4\u56de\u4fe1\u606f\u4e2d\u5305\u542b\u6b64\u5185\u5bb9, \u5219\u8ba4\u4e3a\u6536\u4ef6\u4eba\u4e0d\u5b58\u5728', max_length=50, verbose_name='\u6536\u4ef6\u4eba\u4e0d\u5b58\u5728\u6807\u5fd7')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
        migrations.CreateModel(
            name='NotRetryFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u4e0d\u91cd\u8bd5\u90ae\u4ef6\u6807\u5fd7, \u53d1\u9001\u90ae\u4ef6\u8fd4\u56de\u4fe1\u606f\u4e2d\u5305\u542b\u6b64\u5185\u5bb9, \u5219\u8be5\u90ae\u4ef6\u4e0d\u91cd\u8bd5', max_length=50, verbose_name='\u4e0d\u91cd\u8bd5\u90ae\u4ef6\u6807\u5fd7')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
        migrations.CreateModel(
            name='SpamFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u5783\u573e\u90ae\u4ef6\u6807\u5fd7, \u53d1\u9001\u90ae\u4ef6\u8fd4\u56de\u4fe1\u606f\u4e2d\u5305\u542b\u6b64\u5185\u5bb9, \u5219\u8ba4\u4e3a\u8be5\u90ae\u4ef6\u4e3a\u5783\u573e\u90ae\u4ef6', max_length=50, verbose_name='\u5783\u573e\u90ae\u4ef6\u6807\u5fd7')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
        migrations.CreateModel(
            name='SpfFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='spf\u90ae\u4ef6\u6807\u5fd7, \u53d1\u9001\u90ae\u4ef6\u8fd4\u56de\u4fe1\u606f\u4e2d\u5305\u542b\u6b64\u5185\u5bb9, \u5219\u8ba4\u4e3a\u662fspf\u9519\u8bef\u90ae\u4ef6', max_length=50, verbose_name='spf\u9519\u8bef\u90ae\u4ef6\u6807\u5fd7')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
    ]
