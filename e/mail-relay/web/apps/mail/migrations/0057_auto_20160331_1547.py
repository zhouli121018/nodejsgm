# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0056_attachmenttypeblacklist'),
    ]

    operations = [
        migrations.AddField(
            model_name='checksettings',
            name='collect_attachment_min_size',
            field=models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u7f51\u5173\u5c0f\u5371\u9644\u4ef6\uff1a\u81ea\u52a8\u5220\u9664 \u975e\u4e2d\u6587 \u90ae\u4ef6\u4e2d xxx \u9644\u4ef6\u7c7b\u578b \u4e14 \u5c0f\u4e8eXXX KB\u7684\u90ae\u4ef6\uff0c\u76f4\u63a5\u5220\u9664\uff0c\u4e0d\u5ba1\u6838\uff0c\u4e0d\u5b66\u4e60\u3002\u8fc7\u6ee4\u987a\u5e8f\u5728 \u53d1\u4ef6\u4eba\u767d\u540d\u5355\u68c0\u6d4b \u4e4b\u540e\u3002 \u9ed8\u8ba40KB, \u8868\u793a\u4e0d\u68c0\u6d4b', verbose_name='\u7f51\u5173\u5c0f\u5371\u9644\u4ef6\u9600\u503c'),
        ),
        migrations.AlterField(
            model_name='checksettings',
            name='attachment_min_size',
            field=models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u90ae\u4ef6\u9644\u4ef6\u662frar\u6216zip\u7c7b\u578b\uff0c\u4e14\u5927\u5c0f\u5c0f\u4e8e\u8be5\u9600\u503c, \u5219\u8ba4\u4e3a\u662f\u9ad8\u5371\u90ae\u4ef6, \u9ed8\u8ba40KB, \u8868\u793a\u4e0d\u68c0\u6d4b', verbose_name='\u9ad8\u5371\u9644\u4ef6\u9600\u503c'),
        ),
    ]
