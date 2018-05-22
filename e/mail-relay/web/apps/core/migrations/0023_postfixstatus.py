# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20151203_1617'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostfixStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u65e5\u671f')),
                ('connect_num', models.IntegerField(default=0, verbose_name='\u8fde\u63a5\u6570')),
                ('mail_num', models.IntegerField(default=0, verbose_name='\u90ae\u4ef6\u603b\u6570')),
                ('reject_num', models.IntegerField(default=0, verbose_name='\u62d2\u7edd\u6570')),
                ('pass_num', models.IntegerField(default=0, verbose_name='\u4e2d\u8f6c\u6570')),
                ('rate1', models.IntegerField(default=0, verbose_name='\u9650\u5236\u89c4\u5219\uff11')),
                ('rate2', models.IntegerField(default=0, verbose_name='\u9650\u5236\u89c4\u52192')),
                ('rate3', models.IntegerField(default=0, verbose_name='\u9650\u5236\u89c4\u52193')),
                ('rate4', models.IntegerField(default=0, verbose_name='\u9650\u5236\u89c4\u52194')),
                ('spf', models.IntegerField(default=0, verbose_name='spf')),
                ('rbl', models.IntegerField(default=0, verbose_name='rbl')),
                ('update', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
            ],
        ),
    ]
