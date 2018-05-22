# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0065_bulkcustomer_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checksettings',
            name='collect_attachment_min_size',
            field=models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u5c0f\u5371\u9644\u4ef6\uff1a\u81ea\u52a8\u5220\u9664 \u975e\u4e2d\u6587 \u90ae\u4ef6\u4e2d xxx \u9644\u4ef6\u7c7b\u578b \u4e14 \u5c0f\u4e8eXXX KB\u7684\u90ae\u4ef6\uff0c\u76f4\u63a5\u5220\u9664\uff0c\u4e0d\u5ba1\u6838\uff0c\u4e0d\u5b66\u4e60\u3002\u8fc7\u6ee4\u987a\u5e8f\u5728 \u53d1\u4ef6\u4eba\u767d\u540d\u5355\u68c0\u6d4b \u4e4b\u540e\u3002 \u9ed8\u8ba40KB, \u8868\u793a\u4e0d\u68c0\u6d4b', verbose_name='\u5c0f\u5371\u9644\u4ef6\u9600\u503c'),
        ),
        migrations.AlterField(
            model_name='keywordblacklist',
            name='keyword',
            field=models.CharField(help_text='\u90ae\u4ef6\u5185\u5bb9\u5982\u679c\u542b\u6709\u9ed1\u540d\u5355\u5173\u952e\u8bcd\uff0c\u5219\u5c06\u8be5\u90ae\u4ef6\u6302\u8d77\u5e76\u4ea4\u7ed9\u7ba1\u7406\u5458\u5ba1\u6838,\u652f\u6301\u901a\u914d\u7b26?\uff0c\u4f8b\u5982\u201c\u53d1.{1}\u7968\u201d\u6216\u201c\u53d1.{2}\u7968\u201d\uff0c\u8fd9\u6837\uff0c\u5219\u201c\u53d1a\u7968\u201d \u6216 \u201c\u53d1aa\u7968\u201d', max_length=100, verbose_name='\u5185\u5bb9\u5173\u952e\u5b57'),
        ),
        migrations.AlterField(
            model_name='subjectkeywordblacklist',
            name='keyword',
            field=models.CharField(help_text='\u90ae\u4ef6\u4e3b\u9898\u5982\u679c\u542b\u6709\u9ed1\u540d\u5355\u5173\u952e\u8bcd\uff0c\u5219\u5c06\u8be5\u90ae\u4ef6\u6302\u8d77\u5e76\u4ea4\u7ed9\u7ba1\u7406\u5458\u5ba1\u6838,\u652f\u6301\u901a\u914d\u7b26?\uff0c\u4f8b\u5982\u201c\u53d1.{1}\u7968\u201d\u6216\u201c\u53d1.{2}\u7968\u201d\uff0c\u8fd9\u6837\uff0c\u5219\u201c\u53d1a\u7968\u201d \u6216 \u201c\u53d1aa\u7968\u201d', max_length=100, verbose_name='\u4e3b\u9898\u5173\u952e\u5b57'),
        ),
    ]
