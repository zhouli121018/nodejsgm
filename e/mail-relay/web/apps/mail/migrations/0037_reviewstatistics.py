# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0036_auto_20160129_1521'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewStatistics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u65e5\u671f')),
                ('review_all', models.IntegerField(default=0, verbose_name='\u5168\u90e8\u5ba1\u6838\u6570\u91cf')),
                ('review_pass', models.IntegerField(default=0, verbose_name='\u5ba1\u6838\u901a\u8fc7\u6570\u91cf')),
                ('review_reject', models.IntegerField(default=0, verbose_name='\u5ba1\u6838\u62d2\u7edd\u6570\u91cf')),
                ('review_undo', models.IntegerField(default=0, verbose_name='\u5ba1\u6838\u8bef\u5224\u6570\u91cf')),
                ('review_pass_undo', models.IntegerField(default=0, verbose_name='\u5ba1\u6838\u8bef\u5224\u901a\u8fc7\u6570\u91cf')),
                ('review_reject_undo', models.IntegerField(default=0, verbose_name='\u5ba1\u6838\u8bef\u5224\u62d2\u7edd\u6570\u91cf')),
                ('times', models.IntegerField(default=0, verbose_name='\u5e73\u5747\u5ba1\u6838\u65f6\u957f\uff0c\u5355\u4f4d\u4e3a\u79d2')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
            ],
        ),
    ]
