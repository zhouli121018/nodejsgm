# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0046_auto_20160722_1358'),
    ]

    operations = [
        migrations.CreateModel(
            name='UrlRemark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(help_text='url\u5730\u5740', unique=True, max_length=200, verbose_name='URL')),
                ('remark', models.TextField(null=True, verbose_name='\u5907\u6ce8', blank=True)),
            ],
        ),
    ]
