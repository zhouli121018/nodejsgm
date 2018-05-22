# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0082_auto_20160808_1506'),
    ]

    operations = [
        migrations.CreateModel(
            name='SenderCredit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sender', models.CharField(unique=True, max_length=150, verbose_name='\u53d1\u4ef6\u4eba')),
                ('credit', models.IntegerField(default=1000, verbose_name='\u53d1\u4ef6\u4eba\u4fe1\u8a89\u503c')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
            ],
        ),
        migrations.CreateModel(
            name='SenderCreditLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sender', models.CharField(max_length=150, verbose_name='\u53d1\u4ef6\u4eba')),
                ('mail_id', models.CharField(max_length=20, null=True, verbose_name='\u90ae\u4ef6ID', blank=True)),
                ('expect_value', models.IntegerField(default=0, verbose_name='\u9884\u8ba1\u6263\u9664/\u589e\u52a0\u503c')),
                ('value', models.IntegerField(default=0, verbose_name='\u5b9e\u9645\u6263\u9664/\u589e\u52a0\u503c')),
                ('reason', models.CharField(max_length=20, null=True, verbose_name='\u90ae\u4ef6ID', blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
        migrations.CreateModel(
            name='SenderCreditSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('check_auto_reject', models.IntegerField(default=-5, help_text='\u514d\u5ba1\u62d2\u7edd\u6263\u9664/\u589e\u52a0\u7684\u4fe1\u8a89\u5ea6\u503c', verbose_name='\u514d\u5ba1\u62d2\u7edd')),
                ('check_dspam', models.IntegerField(default=-5, help_text='\u88abdspam\u68c0\u6d4b\u6263\u9664/\u589e\u52a0\u7684\u4fe1\u8a89\u5ea6\u503c', verbose_name='Dspam')),
                ('send_spam', models.IntegerField(default=-5, help_text='\u53d1\u9001\u5783\u573e\u90ae\u4ef6\u6263\u9664/\u589e\u52a0\u7684\u4fe1\u8a89\u5ea6\u503c', verbose_name='\u53d1\u9001\u5783\u573e\u90ae\u4ef6')),
                ('send_not_exist', models.IntegerField(default=-5, help_text='\u53d1\u9001\u4e0d\u5b58\u5728\u90ae\u4ef6\u6263\u9664/\u589e\u52a0\u7684\u4fe1\u8a89\u5ea6\u503c', verbose_name='\u53d1\u9001\u4e0d\u5b58\u5728\u90ae\u4ef6')),
                ('review_reject', models.IntegerField(default=-5, help_text='\u5ba1\u6838\u62d2\u7edd\u6263\u9664/\u589e\u52a0\u7684\u4fe1\u8a89\u5ea6\u503c', verbose_name='\u5ba1\u6838\u62d2\u7edd')),
                ('review_pass', models.IntegerField(default=1, help_text='\u5ba1\u6838\u901a\u8fc7\u6263\u9664/\u589e\u52a0\u7684\u4fe1\u8a89\u5ea6\u503c', verbose_name='\u5ba1\u6838\u901a\u8fc7')),
                ('increase_limit', models.IntegerField(default=10, help_text='\u9ed8\u8ba410', verbose_name='\u5f53\u5929\u6700\u5927\u589e\u52a0\u503c')),
                ('reduce_limit', models.IntegerField(default=100, help_text='\u9ed8\u8ba4100', verbose_name='\u5f53\u5929\u6700\u5927\u6263\u9664\u503c')),
            ],
        ),
    ]
