# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-12 11:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SendContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('send_content', models.TextField(verbose_name='\u90ae\u4ef6')),
            ],
            options={
                'db_table': 'ms_send_content',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SendTask',
            fields=[
                ('id', models.AutoField(db_column='send_id', primary_key=True, serialize=False)),
                ('send_name', models.CharField(blank=True, max_length=35, null=True, verbose_name='\u4efb\u52a1\u540d\u79f0')),
                ('send_acct_type', models.CharField(blank=True, choices=[('all', '\u6240\u6709\u57df\u540d'), ('domain', '\u5355\u4e2a\u57df\u540d')], default='all', max_length=10, null=True, verbose_name='\u53d1\u9001\u8d26\u53f7\u7c7b\u578b')),
                ('send_acct_domain', models.CharField(blank=True, default='all', max_length=60, null=True, verbose_name='\u53d1\u9001\u8d26\u53f7\u57df\u540d')),
                ('send_acct_address', models.CharField(blank=True, max_length=70, null=True, verbose_name='\u53d1\u9001\u5730\u5740')),
                ('send_account', models.CharField(blank=True, max_length=50, null=True, verbose_name='\u53d1\u9001\u8d26\u53f7')),
                ('send_replyto', models.CharField(blank=True, max_length=50, null=True, verbose_name='\u6307\u5b9a\u56de\u590d\u5730\u5740')),
                ('send_fullname', models.CharField(blank=True, max_length=50, null=True, verbose_name='\u53d1\u9001\u4eba\u540d\u79f0')),
                ('send_template', models.CharField(blank=True, max_length=100, null=True, verbose_name='\u6a21\u677f\u540d\u79f0')),
                ('send_template_id', models.IntegerField(blank=True, default=0, null=True, verbose_name='\u6a21\u677fID')),
                ('send_maillist', models.CharField(blank=True, max_length=100, null=True, verbose_name='\u53d1\u9001\u90ae\u4ef6\u5217\u8868\u540d')),
                ('send_maillist_id', models.IntegerField(blank=True, null=True, verbose_name='\u53d1\u9001\u90ae\u4ef6\u5217\u8868\u540dID')),
                ('send_qty_start', models.IntegerField(default=0, verbose_name='\u53d1\u9001\u5f00\u59cb\u6570\u91cf')),
                ('send_qty', models.IntegerField(default=0, verbose_name='\u53d1\u9001\u5217\u8868\u90ae\u7bb1\u6570\u91cf')),
                ('send_qty_remark', models.IntegerField(default=0, verbose_name='\u53d1\u9001\u5217\u8868\u90ae\u7bb1\u6570\u91cf')),
                ('send_time', models.DateTimeField(auto_now=True, null=True, verbose_name='\u4efb\u52a1\u53d1\u9001\u65f6\u95f4')),
                ('send_status', models.SmallIntegerField(choices=[(-2, '\u6682\u505c\u53d1\u9001'), (-1, '\u53d1\u9001\u51fa\u9519'), (0, '\u7b49\u5f85\u53d1\u9001'), (1, '\u7b49\u5f85\u53d1\u9001'), (2, '\u6b63\u5728\u53d1\u9001'), (3, '\u53d1\u9001\u5b8c\u6210')], default=0, verbose_name='\u4efb\u52a1\u72b6\u6001')),
                ('verify_status', models.SmallIntegerField(choices=[(0, '\u7b49\u5f85\u5ba1\u6838'), (1, '\u7b49\u5f85\u901a\u8fc7')], default=1, verbose_name='\u5ba1\u6838\u72b6\u6001')),
                ('send_count', models.IntegerField(default=0, verbose_name='\u6210\u529f\u53d1\u9001\u6570')),
                ('error_count', models.IntegerField(default=0, verbose_name='\u53d1\u9001\u5931\u8d25\u6570')),
                ('time_start', models.DateTimeField(auto_now=True, null=True, verbose_name='\u4efb\u52a1\u5f00\u59cb\u65f6\u95f4')),
                ('time_end', models.DateTimeField(auto_now=True, null=True, verbose_name='\u4efb\u52a1\u7ed3\u675f\u65f6\u95f4')),
                ('track_status', models.SmallIntegerField(choices=[(0, '\u4e0d\u8ddf\u8e2a'), (1, '\u8ddf\u8e2a\u90ae\u4ef6\u6253\u5f00\u60c5\u51b5'), (2, '\u8ddf\u8e2a\u90ae\u4ef6\u6253\u5f00\u4e0e\u94fe\u63a5\u70b9\u51fb\u60c5\u51b5')], default=0, verbose_name='\u8ddf\u8e2a\u72b6\u6001')),
                ('track_domain', models.CharField(blank=True, help_text='\u5ba2\u6237\u6307\u5b9a\u57df\u540d\uff0c\u66ff\u6362\u8ddf\u8e2a\u7edf\u8ba1\u94fe\u63a5\u57df\u540d', max_length=100, null=True, verbose_name='\u5ba2\u6237\u6307\u5b9a\u57df\u540d')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('isvalid', models.BooleanField(default=True, verbose_name='\u662f\u5426\u6709\u6548')),
            ],
            options={
                'db_table': 'ms_send_list',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SendTaskState',
            fields=[
                ('id', models.AutoField(db_column='task_id', primary_key=True, serialize=False)),
                ('task_date', models.DateField(blank=True, null=True)),
                ('send_name', models.CharField(blank=True, db_column='task_ident', max_length=35, null=True, verbose_name='\u4efb\u52a1\u540d\u79f0')),
                ('count_send', models.IntegerField(default=0, verbose_name='\u53d1\u9001\u603b\u6570')),
            ],
            options={
                'db_table': 'stat_task',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SendTaskTpl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('send_count', models.IntegerField(default=0, verbose_name='\u53d1\u9001\u6570\u91cf')),
                ('send_success', models.IntegerField(default=0, verbose_name='\u6210\u529f\u6570\u91cf')),
            ],
            options={
                'db_table': 'ms_send_list_tpl',
                'managed': False,
            },
        ),
    ]