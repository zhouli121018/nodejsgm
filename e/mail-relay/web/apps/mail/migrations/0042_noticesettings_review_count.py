# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0041_auto_20160307_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='noticesettings',
            name='review_count',
            field=models.IntegerField(default=200, help_text='\u9700\u5ba1\u6838\u90ae\u4ef6\u7684\u5c01\u6570\uff08\u4e2d\u7ee7+\u7f51\u5173-cyber\uff09\uff0c\u5f53\u8d85\u8fc7\u8be5\u503c\u65f6\uff0c\u53d1\u9001\u76f8\u5e94\u901a\u77e5', verbose_name='\u5ba1\u6838\u6570\u9600\u503c'),
        ),
    ]
