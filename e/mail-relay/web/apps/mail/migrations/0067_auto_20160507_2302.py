# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0066_auto_20160507_2242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachmentblacklist',
            name='keyword',
            field=models.CharField(help_text='\u5bf9\u9644\u4ef6\u8fdb\u884c\u68c0\u6d4b\uff0c\u5982\u679c\u9644\u4ef6\u540d\u79f0\u5305\u542b\u9ed1\u540d\u5355\u5173\u952e\u8bcd,\u3000\u5219\u5c06\u90ae\u4ef6\u6807\u5fd7\u4e3a\u9ad8\u5371\u90ae\u4ef6\u5ba1\u6838\u3002\u652f\u6301\u6b63\u5219', max_length=100, verbose_name='\u9644\u4ef6\u5173\u952e\u5b57'),
        ),
    ]
