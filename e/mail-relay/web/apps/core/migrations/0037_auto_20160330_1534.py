# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_customersetting_notice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersetting',
            name='notice',
            field=models.BooleanField(default=True, help_text='\u9009\u4e2d\u5373\u4e3a\u5f00\u542f\uff0c\u5f53\u5173\u95ed\u65f6\uff0c\u8be5\u7528\u6237\u8d26\u53f7\u4e0d\u53d1\u77ed\u4fe1/\u90ae\u4ef6\u901a\u77e5', verbose_name='\u77ed\u4fe1/\u90ae\u4ef6\u6d88\u606f\u901a\u77e5\u5f00\u5173'),
        ),
    ]
