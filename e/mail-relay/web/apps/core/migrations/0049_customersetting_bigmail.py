# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0048_auto_20160802_1729'),
    ]

    operations = [
        migrations.AddField(
            model_name='customersetting',
            name='bigmail',
            field=models.BooleanField(default=False, help_text='\u5982\u679c\u5f00\u542f\uff1a\u53d1\u9001\u540e\u65e5\u5fd7\u663e\u793a\u90ae\u4ef6\u8d85\u5927\u6ee1\u7684\u90ae\u4ef6\uff0c\u5219\u81ea\u52a8\u8f6c\u94fe\u63a5\u65b9\u5f0f\uff08\u53d1\u9001\u4e00\u6b21\uff0c\u5982\u679c\u8fd8\u4e0d\u6210\u529f\u5219\u4e0d\u5c1d\u8bd5\uff09\uff0c\u9644\u4ef6\u4fdd\u7559\u5728\u670d\u52a1\u5668\u4e0a\uff0c\u9644\u4ef6\u4fdd\u7559\u65f6\u95f4\u4e3aX\u5929\u3002', verbose_name='\u4e2d\u7ee7:\u8d85\u5927\u90ae\u4ef6\u81ea\u52a8\u8f6c\u7f51\u7edc\u94fe\u63a5\u53d1\u9001'),
        ),
    ]
