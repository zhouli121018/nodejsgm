# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20151113_1416'),
        ('mail', '0017_auto_20151111_1430'),
    ]

    operations = [
        migrations.CreateModel(
            name='BulkCustomer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('spam_count', models.IntegerField(default=0, verbose_name='\u5783\u573e\u90ae\u4ef6\u6570')),
                ('sender', models.TextField(verbose_name='\u5783\u573e\u90ae\u4ef6\u6570')),
                ('sender_count', models.IntegerField(default=0, verbose_name='\u5783\u573e\u90ae\u4ef6\u6570')),
                ('recent_count', models.IntegerField(default=0, verbose_name='\u6700\u8fd1\u53d1\u9001\u6b21\u6570')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Customer', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='settings',
            name='bulk_customer',
            field=models.IntegerField(default=1000, help_text='\u6bcf\u5929\u201c\u7fa4\u53d1+DSPAM+\u683c\u9519+\u6536\u9ed1\u201d \u6570\u8d85\u8fc7X\u7684\u5ba2\u6237\u6807\u5fd7\u4e3a\u7fa4\u53d1\u5ba2\u6237', verbose_name='\u7fa4\u53d1\u5ba2\u6237\u9600\u503c'),
        ),
    ]
