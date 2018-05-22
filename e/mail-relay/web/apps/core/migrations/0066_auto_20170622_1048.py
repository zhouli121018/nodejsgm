# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0065_auto_20170615_0922'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerSummary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u65e5\u671f')),
                ('relay_count', models.IntegerField(default=0, verbose_name='\u4e2d\u7ee7\u53d1\u4ef6\u4eba\u6570\u91cf')),
                ('relay_limit', models.IntegerField(default=0, verbose_name='\u4e2d\u7ee7\u7528\u6237\u6570')),
                ('is_relay_limit', models.BooleanField(default=0, verbose_name='\u4e2d\u7ee7\u662f\u5426\u8d85\u9650')),
                ('collect_count', models.IntegerField(default=0, verbose_name='\u7f51\u5173\u6536\u4ef6\u4eba\u6570\u91cf')),
                ('collect_limit', models.IntegerField(default=0, verbose_name='\u7f51\u5173\u7528\u6237\u6570')),
                ('is_collect_limit', models.BooleanField(default=0, verbose_name='\u7f51\u5173\u662f\u5426\u8d85\u9650')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='collect_exceed',
            field=models.IntegerField(default=0, verbose_name='\u7f51\u5173\u8d85\u9650\u6b21\u6570'),
        ),
        migrations.AddField(
            model_name='customer',
            name='relay_exceed',
            field=models.IntegerField(default=0, verbose_name='\u4e2d\u7ee7\u8d85\u9650\u6b21\u6570'),
        ),
        migrations.AddField(
            model_name='customersummary',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to='core.Customer', null=True),
        ),
    ]
