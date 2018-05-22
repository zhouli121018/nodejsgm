# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0046_auto_20160316_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='keywordblacklist',
            name='c_direct_reject',
            field=models.BooleanField(default=False, verbose_name='\u7f51\u5173,\u662f\u5426\u4e0d\u7528\u5ba1\u6838\uff0c\u76f4\u63a5\u62d2\u7edd'),
        ),
        migrations.AlterField(
            model_name='keywordblacklist',
            name='direct_reject',
            field=models.BooleanField(default=False, verbose_name='\u4e2d\u7ee7,\u662f\u5426\u4e0d\u7528\u5ba1\u6838\uff0c\u76f4\u63a5\u62d2\u7edd'),
        ),
    ]
