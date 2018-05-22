# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0020_senderwhitelist'),
    ]

    operations = [
        migrations.AddField(
            model_name='checksettings',
            name='ctasd_max_size',
            field=models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u90ae\u4ef6\u5982\u679c\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u76f4\u63a5\u653e\u884c, \u4e0d\u8fdb\u884c\u68c0\u6d4b, \u9ed8\u8ba40KB, \u8868\u793a\u5168\u90e8\u68c0\u6d4b', verbose_name='Ctasd\u68c0\u6d4b\u9600\u503c'),
        ),
    ]
