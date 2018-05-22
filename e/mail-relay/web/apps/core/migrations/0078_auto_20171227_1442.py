# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0077_auto_20171226_0902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersetting',
            name='spamrpt_sendtime',
            field=models.TimeField(help_text='\u5c06\u8be5\u65f6\u95f4\u4ee5\u524d\u768424\u4e2a\u5c0f\u65f6\u5185\u6240\u6709\u7684\u62d2\u7edd\u90ae\u4ef6\uff0c\u4ee5\u62a5\u544a\u5f62\u5f0f\u5728\u8be5\u65f6\u95f4\u53d1\u9001\uff0c\u800c\u4e14\u4e0d\u4f1a\u5728\u9ed8\u8ba4\u7684\u96f6\u70b9\u53d1\u9001\u4e86', null=True, verbose_name='\u9694\u79bb\u62a5\u544a\u53d1\u9001\u65f6\u95f4', blank=True),
        ),
    ]
