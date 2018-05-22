# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mail', '0094_edmchecksettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectRecipientWhitelist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u7f51\u5173\u6536\u4ef6\u4eba\u767d\u540d\u5355, \u5982\u679c\u6536\u4ef6\u4eba\u5728\u767d\u540d\u5355\u4e2d\uff0c\u7f51\u5173\u5bf9\u8be5\u53d1\u4ef6\u4eba\u4e0d\u505a\u4efb\u4f55\u8fc7\u6ee4', unique=True, max_length=50, verbose_name='\u6536\u4ef6\u4eba')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('operate_time', models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True)),
                ('creater', models.ForeignKey(related_name='creater30', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('operater', models.ForeignKey(related_name='operater30', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='recipientwhitelist',
            name='keyword',
            field=models.CharField(help_text='\u4e2d\u7ee7\u6536\u4ef6\u4eba\u767d\u540d\u5355, \u5982\u679c\u6536\u4ef6\u4eba\u5728\u767d\u540d\u5355\u4e2d\uff0c\u53ea\u505aDSPAM\u8fc7\u6ee4\uff0c\u7136\u540e\u5c31\u76f4\u63a5\u53d1\u9001\uff1b\u4e0d\u652f\u6301\u6b63\u5219\u6807\u51c6,\u652f\u6301\u6574\u57df\u540d\u8fc7\u6ee4\uff0c\u5982test.com\u4e14\u4e0b\u9762\u9009\u4e2d\u4e3a\u57df\u540d\uff0c\u8868\u793a\u6574\u4e2atest.com\u4e3a\u57df\u540d\u7684\u6536\u4ef6\u4eba\u4e3a\u767d\u540d\u5355\u6536\u4ef6\u4eba', unique=True, max_length=50, verbose_name='\u6536\u4ef6\u4eba'),
        ),
    ]
