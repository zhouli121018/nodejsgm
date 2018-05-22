# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_colcustomerdomain'),
    ]

    operations = [
        migrations.AddField(
            model_name='customersetting',
            name='check_content',
            field=models.BooleanField(default=True, verbose_name='\u7f51\u5173\u8fc7\u6ee4:\u5185\u5bb9\u5173\u952e\u5b57'),
        ),
        migrations.AddField(
            model_name='customersetting',
            name='check_ctasd',
            field=models.BooleanField(default=True, verbose_name='\u7f51\u5173\u8fc7\u6ee4:cyber'),
        ),
        migrations.AddField(
            model_name='customersetting',
            name='check_dspam',
            field=models.BooleanField(default=True, verbose_name='\u7f51\u5173\u8fc7\u6ee4:dspam'),
        ),
        migrations.AddField(
            model_name='customersetting',
            name='check_high_risk',
            field=models.BooleanField(default=True, verbose_name='\u7f51\u5173\u8fc7\u6ee4:\u9ad8\u5371\u90ae\u4ef6'),
        ),
        migrations.AddField(
            model_name='customersetting',
            name='check_sender',
            field=models.BooleanField(default=True, verbose_name='\u7f51\u5173\u8fc7\u6ee4:\u53d1\u4ef6\u4eba\u9ed1\u540d\u5355'),
        ),
        migrations.AddField(
            model_name='customersetting',
            name='check_spam',
            field=models.BooleanField(default=True, verbose_name='\u7f51\u5173\u8fc7\u6ee4:spamassassion'),
        ),
        migrations.AddField(
            model_name='customersetting',
            name='check_subject',
            field=models.BooleanField(default=True, verbose_name='\u7f51\u5173\u8fc7\u6ee4:\u4e3b\u9898\u5173\u952e\u5b57'),
        ),
    ]
