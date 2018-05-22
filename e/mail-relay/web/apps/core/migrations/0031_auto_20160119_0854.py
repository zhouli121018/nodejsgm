# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_customer_support_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='postfixstatus',
            name='rate5',
            field=models.IntegerField(default=0, verbose_name='\u9650\u5236\u89c4\u52195(10\u5206\u949f)'),
        ),
        migrations.AddField(
            model_name='postfixstatus',
            name='rate6',
            field=models.IntegerField(default=0, verbose_name='\u9650\u5236\u89c4\u52196(6\u5c0f\u65f6)'),
        ),
        migrations.AddField(
            model_name='postfixstatus',
            name='rate7',
            field=models.IntegerField(default=0, verbose_name='\u9650\u5236\u89c4\u52197(12\u5c0f\u65f6)'),
        ),
        migrations.AddField(
            model_name='postfixstatus',
            name='rate8',
            field=models.IntegerField(default=0, verbose_name='\u9650\u5236\u89c4\u52198(24\u5c0f\u65f6)'),
        ),
        migrations.AddField(
            model_name='postfixstatus',
            name='server_id',
            field=models.CharField(default=b'shenzhen', max_length=20, verbose_name='\u6240\u5728\u670d\u52a1\u5668\u7684ID', db_index=True, choices=[(b'shenzhen', '\u6df1\u5733'), (b'hangzhou', '\u676d\u5dde')]),
        ),
        migrations.AlterField(
            model_name='postfixstatus',
            name='rate1',
            field=models.IntegerField(default=0, verbose_name='\u9650\u5236\u89c4\u5219\uff11(20\u5206\u949f)'),
        ),
        migrations.AlterField(
            model_name='postfixstatus',
            name='rate2',
            field=models.IntegerField(default=0, verbose_name='\u9650\u5236\u89c4\u52192(30\u5206\u949f)'),
        ),
        migrations.AlterField(
            model_name='postfixstatus',
            name='rate3',
            field=models.IntegerField(default=0, verbose_name='\u9650\u5236\u89c4\u52193(1\u5c0f\u65f6)'),
        ),
        migrations.AlterField(
            model_name='postfixstatus',
            name='rate4',
            field=models.IntegerField(default=0, verbose_name='\u9650\u5236\u89c4\u52194(3\u5c0f\u65f6)'),
        ),
    ]
