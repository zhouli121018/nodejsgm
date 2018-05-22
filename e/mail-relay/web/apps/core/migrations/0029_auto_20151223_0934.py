# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20151222_1711'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='contact',
            field=models.CharField(max_length=20, null=True, verbose_name='\u8054\u7cfb\u4eba', blank=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='email',
            field=models.EmailField(max_length=20, null=True, verbose_name='\u90ae\u7bb1', blank=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='emergency_contact',
            field=models.CharField(max_length=20, null=True, verbose_name='\u7d27\u6025\u8054\u7cfb\u4eba', blank=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='emergency_mobile',
            field=models.CharField(max_length=20, null=True, verbose_name='\u7d27\u6025\u8054\u7cfb\u4eba\u624b\u673a', blank=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='mobile',
            field=models.CharField(max_length=20, null=True, verbose_name='\u8054\u7cfb\u4eba\u624b\u673a', blank=True),
        ),
    ]
