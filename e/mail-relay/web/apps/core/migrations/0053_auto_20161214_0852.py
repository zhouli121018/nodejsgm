# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0052_auto_20161115_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='gateway_service_end',
            field=models.DateField(null=True, verbose_name='\u7f51\u5173\u670d\u52a1\u5230\u671f\u65f6\u95f4', blank=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='gateway_service_start',
            field=models.DateField(null=True, verbose_name='\u7f51\u5173\u670d\u52a1\u5f00\u59cb\u65f6\u95f4', blank=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='service_end',
            field=models.DateField(null=True, verbose_name='\u4e2d\u7ee7\u670d\u52a1\u5230\u671f\u65f6\u95f4', blank=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='service_start',
            field=models.DateField(null=True, verbose_name='\u4e2d\u7ee7\u670d\u52a1\u5f00\u59cb\u65f6\u95f4', blank=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='status',
            field=models.CharField(default=b'normal', max_length=10, verbose_name='\u4e2d\u7ee7\u72b6\u6001', choices=[(b'', '--'), (b'normal', '\u6b63\u5e38'), (b'expiring', '\u5373\u5c06\u8fc7\u671f'), (b'expired', '\u5df2\u8fc7\u671f'), (b'disabled', '\u5df2\u7981\u7528')]),
        ),
    ]
