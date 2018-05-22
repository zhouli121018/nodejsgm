# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0035_checkstatistics'),
    ]

    operations = [
        migrations.AddField(
            model_name='keywordblacklist',
            name='collect_all',
            field=models.IntegerField(default=0, verbose_name='\u7f51\u5173\u68c0\u6d4b\u6570'),
        ),
        migrations.AddField(
            model_name='keywordblacklist',
            name='collect_pass',
            field=models.IntegerField(default=0, verbose_name='\u7f51\u5173\u901a\u8fc7\u6570'),
        ),
        migrations.AddField(
            model_name='keywordblacklist',
            name='relay_all',
            field=models.IntegerField(default=0, verbose_name='\u4e2d\u7ee7\u68c0\u6d4b\u6570'),
        ),
        migrations.AddField(
            model_name='keywordblacklist',
            name='relay_pass',
            field=models.IntegerField(default=0, verbose_name='\u4e2d\u7ee7\u901a\u8fc7\u6570'),
        ),
        migrations.AddField(
            model_name='subjectkeywordblacklist',
            name='collect_all',
            field=models.IntegerField(default=0, verbose_name='\u7f51\u5173\u68c0\u6d4b\u6570'),
        ),
        migrations.AddField(
            model_name='subjectkeywordblacklist',
            name='collect_pass',
            field=models.IntegerField(default=0, verbose_name='\u7f51\u5173\u901a\u8fc7\u6570'),
        ),
        migrations.AddField(
            model_name='subjectkeywordblacklist',
            name='relay_all',
            field=models.IntegerField(default=0, verbose_name='\u4e2d\u7ee7\u68c0\u6d4b\u6570'),
        ),
        migrations.AddField(
            model_name='subjectkeywordblacklist',
            name='relay_pass',
            field=models.IntegerField(default=0, verbose_name='\u4e2d\u7ee7\u901a\u8fc7\u6570'),
        ),
    ]
