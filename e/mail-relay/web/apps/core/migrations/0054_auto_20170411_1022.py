# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_auto_20161214_0852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersetting',
            name='can_view_mail',
            field=models.BooleanField(default=False, verbose_name='\u7528\u6237\u662f\u5426\u53ef\u4ee5\u67e5\u770b\u90ae\u4ef6'),
        ),
        migrations.AlterField(
            model_name='customersetting',
            name='check_level',
            field=models.CharField(default=b'intermediate', max_length=20, verbose_name='\u7f51\u5173\u8fc7\u6ee4\u7ea7\u522b', choices=[(b'', '--'), (b'basic', '\u57fa\u7840\u53cd\u5783\u573e'), (b'intermediate', '\u4e2d\u7ea7\u53cd\u5783\u573e'), (b'senior', '\u9ad8\u7ea7\u53cd\u5783\u573e')]),
        ),
        migrations.AlterField(
            model_name='customersetting',
            name='customer',
            field=models.ForeignKey(to='core.Customer', unique=True),
        ),
    ]
