# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_customer_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='customersetting',
            name='check_level',
            field=models.CharField(default=b'senior', max_length=20, verbose_name='\u7f51\u5173\u8fc7\u6ee4\u7ea7\u522b', choices=[(b'basic', '\u57fa\u7840\u53cd\u5783\u573e'), (b'intermediate', '\u4e2d\u7ea7\u53cd\u5783\u573e'), (b'senior', '\u9ad8\u7ea7\u53cd\u5783\u573e')]),
        ),
    ]
