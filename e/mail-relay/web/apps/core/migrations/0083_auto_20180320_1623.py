# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0082_auto_20180320_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersummary',
            name='all_flow',
            field=models.BigIntegerField(default=0, verbose_name=b'\xe6\x80\xbb\xe5\x85\xb1\xe6\xb5\x81\xe9\x87\x8f'),
        ),
        migrations.AlterField(
            model_name='customersummary',
            name='c_all_flow',
            field=models.BigIntegerField(default=0, verbose_name=b'\xe6\x80\xbb\xe5\x85\xb1\xe6\xb5\x81\xe9\x87\x8f'),
        ),
        migrations.AlterField(
            model_name='customersummary',
            name='c_fail_finished_flow',
            field=models.BigIntegerField(default=0, verbose_name=b'\xe5\xa4\xb1\xe8\xb4\xa5\xe6\x80\xbb\xe5\x85\xb1\xe6\xb5\x81\xe9\x87\x8f'),
        ),
        migrations.AlterField(
            model_name='customersummary',
            name='c_finished_flow',
            field=models.BigIntegerField(default=0, verbose_name=b'\xe6\x88\x90\xe5\x8a\x9f\xe6\x80\xbb\xe5\x85\xb1\xe6\xb5\x81\xe9\x87\x8f'),
        ),
        migrations.AlterField(
            model_name='customersummary',
            name='c_out_all_flow',
            field=models.BigIntegerField(default=0, verbose_name=b'\xe5\x87\xba\xe7\xab\x99\xe6\x80\xbb\xe5\x85\xb1\xe6\xb5\x81\xe9\x87\x8f'),
        ),
        migrations.AlterField(
            model_name='customersummary',
            name='c_reject_flow',
            field=models.BigIntegerField(default=0, verbose_name=b'\xe8\xbf\x87\xe6\xbb\xa4\xe6\x80\xbb\xe5\x85\xb1\xe6\xb5\x81\xe9\x87\x8f'),
        ),
        migrations.AlterField(
            model_name='customersummary',
            name='fail_finished_flow',
            field=models.BigIntegerField(default=0, verbose_name=b'\xe5\xa4\xb1\xe8\xb4\xa5\xe6\x80\xbb\xe5\x85\xb1\xe6\xb5\x81\xe9\x87\x8f'),
        ),
        migrations.AlterField(
            model_name='customersummary',
            name='finished_flow',
            field=models.BigIntegerField(default=0, verbose_name=b'\xe6\x88\x90\xe5\x8a\x9f\xe6\x80\xbb\xe5\x85\xb1\xe6\xb5\x81\xe9\x87\x8f'),
        ),
        migrations.AlterField(
            model_name='customersummary',
            name='out_all_flow',
            field=models.BigIntegerField(default=0, verbose_name=b'\xe5\x87\xba\xe7\xab\x99\xe6\x80\xbb\xe5\x85\xb1\xe6\xb5\x81\xe9\x87\x8f'),
        ),
        migrations.AlterField(
            model_name='customersummary',
            name='reject_flow',
            field=models.BigIntegerField(default=0, verbose_name=b'\xe8\xbf\x87\xe6\xbb\xa4\xe6\x80\xbb\xe5\x85\xb1\xe6\xb5\x81\xe9\x87\x8f'),
        ),
    ]
