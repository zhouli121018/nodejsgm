# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0078_auto_20171227_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='customersetting',
            name='interval_spamrpt',
            field=models.IntegerField(default=0, help_text='\u5355\u4f4d\u5c0f\u65f6\uff0c\u6bcfX\u4e2a\u5c0f\u65f6\u53d1\u9001X\u5c0f\u65f6\u4ee5\u524d\u7684\u9694\u79bb\u62a5\u544a\u5185\u5bb9', verbose_name='\u7f51\u5173:\u9694\u79bb\u62a5\u544a\u53d1\u9001\u95f4\u9694'),
        ),
    ]
