# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0078_auto_20160720_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipientwhitelist',
            name='keyword',
            field=models.CharField(help_text='\u6536\u4ef6\u4eba\u767d\u540d\u5355, \u5982\u679c\u6536\u4ef6\u4eba\u5728\u767d\u540d\u5355\u4e2d\uff0c\u53ea\u505aDSPAM\u8fc7\u6ee4\uff0c\u7136\u540e\u5c31\u76f4\u63a5\u53d1\u9001\uff1b\u4e0d\u652f\u6301\u6b63\u5219\u6807\u51c6,\u652f\u6301\u6574\u57df\u540d\u8fc7\u6ee4\uff0c\u5982test.com\u4e14\u4e0b\u9762\u9009\u4e2d\u4e3a\u57df\u540d\uff0c\u8868\u793a\u6574\u4e2atest.com\u4e3a\u57df\u540d\u7684\u6536\u4ef6\u4eba\u4e3a\u767d\u540d\u5355\u6536\u4ef6\u4eba', unique=True, max_length=50, verbose_name='\u6536\u4ef6\u4eba'),
        ),
    ]
