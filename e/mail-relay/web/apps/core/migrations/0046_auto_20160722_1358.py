# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0045_auto_20160718_0904'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='collect_limit',
            field=models.IntegerField(default=0, verbose_name='\u7f51\u5173\u7528\u6237\u6570(\u6536\u4ef6\u4eba)'),
        ),
        migrations.AddField(
            model_name='customer',
            name='relay_limit',
            field=models.IntegerField(default=0, verbose_name='\u4e2d\u7ee7\u7528\u6237\u6570(\u53d1\u4ef6\u4eba)'),
        ),
    ]
