# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0059_customersetting_replace_sender'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='lang_code',
            field=models.CharField(default=b'zh-cn', max_length=10, verbose_name='\u7528\u6237\u8bed\u8a00', choices=[(b'en', 'English'), (b'zh-cn', '\u4e2d\u6587\u7b80\u4f53')]),
        ),
    ]
