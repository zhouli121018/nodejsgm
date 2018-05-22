# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0079_customersetting_interval_spamrpt'),
    ]

    operations = [
        migrations.AddField(
            model_name='customersummary',
            name='all',
            field=models.IntegerField(default=0, verbose_name=b'\xe6\x80\xbb\xe5\x85\xb1\xe6\x95\xb0\xe9\x87\x8f'),
        ),
        migrations.AddField(
            model_name='customersummary',
            name='all_flow',
            field=models.IntegerField(default=0, verbose_name=b'\xe6\x80\xbb\xe5\x85\xb1\xe6\xb5\x81\xe9\x87\x8f'),
        ),
        migrations.AddField(
            model_name='customersummary',
            name='fail',
            field=models.IntegerField(default=0, verbose_name=b'\xe5\xa4\xb1\xe8\xb4\xa5\xe6\x80\xbb\xe5\x85\xb1\xe6\x95\xb0\xe9\x87\x8f'),
        ),
        migrations.AddField(
            model_name='customersummary',
            name='fail_flow',
            field=models.IntegerField(default=0, verbose_name=b'\xe5\xa4\xb1\xe8\xb4\xa5\xe6\x80\xbb\xe5\x85\xb1\xe6\xb5\x81\xe9\x87\x8f'),
        ),
        migrations.AddField(
            model_name='customersummary',
            name='out_all',
            field=models.IntegerField(default=0, verbose_name=b'\xe5\x87\xba\xe7\xab\x99\xe6\x80\xbb\xe5\x85\xb1\xe6\x95\xb0\xe9\x87\x8f'),
        ),
        migrations.AddField(
            model_name='customersummary',
            name='out_all_flow',
            field=models.IntegerField(default=0, verbose_name=b'\xe5\x87\xba\xe7\xab\x99\xe6\x80\xbb\xe5\x85\xb1\xe6\xb5\x81\xe9\x87\x8f'),
        ),
        migrations.AddField(
            model_name='customersummary',
            name='reject',
            field=models.IntegerField(default=0, verbose_name=b'\xe8\xbf\x87\xe6\xbb\xa4\xe6\x80\xbb\xe5\x85\xb1\xe6\x95\xb0\xe9\x87\x8f'),
        ),
        migrations.AddField(
            model_name='customersummary',
            name='reject_flow',
            field=models.IntegerField(default=0, verbose_name=b'\xe8\xbf\x87\xe6\xbb\xa4\xe6\x80\xbb\xe5\x85\xb1\xe6\xb5\x81\xe9\x87\x8f'),
        ),
        migrations.AddField(
            model_name='customersummary',
            name='success',
            field=models.IntegerField(default=0, verbose_name=b'\xe6\x88\x90\xe5\x8a\x9f\xe6\x80\xbb\xe5\x85\xb1\xe6\x95\xb0\xe9\x87\x8f'),
        ),
        migrations.AddField(
            model_name='customersummary',
            name='success_flow',
            field=models.IntegerField(default=0, verbose_name=b'\xe6\x88\x90\xe5\x8a\x9f\xe6\x80\xbb\xe5\x85\xb1\xe6\xb5\x81\xe9\x87\x8f'),
        ),
        migrations.AddField(
            model_name='customersummary',
            name='total_all',
            field=models.IntegerField(default=0, help_text='\u90ae\u4ef6\u5c01\u6570mail_id=0', verbose_name=b'\xe6\x80\xbb\xe5\x85\xb1\xe6\x95\xb0\xe9\x87\x8f'),
        ),
    ]
