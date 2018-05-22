# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0009_auto_20150925_0925'),
    ]

    operations = [
        migrations.AddField(
            model_name='checksettings',
            name='auto_review_expire',
            field=models.IntegerField(default=365, help_text='\u5355\u4f4d\uff1a\u5929\u6570, \u81ea\u52a8\u5ba1\u6838\u4e2d\uff0c\u53d1\u4ef6\u4eba-\u6536\u4ef6\u4eba\u5bf9\u5e94\u5173\u7cfb\u8fc7\u671f\u65f6\u95f4', verbose_name='\u81ea\u52a8\u5ba1\u6838\u5bf9\u5e94\u5173\u7cfb\u8fc7\u671f\u65f6\u95f4'),
        ),
        migrations.AddField(
            model_name='checksettings',
            name='auto_review_num',
            field=models.IntegerField(default=10, help_text='\u5355\u4f4d\uff1a\u64cd\u4f5c\u6b21\u6570, \u81ea\u52a8\u5ba1\u6838\u4e2d\uff0c\u53d1\u4ef6\u4eba-\u6536\u4ef6\u4eba\u8fde\u7eedX\u6b21\u901a\u8fc7/\u62d2\u7edd,\u5219\u8bb0\u5f55\u76f8\u5e94\u5173\u7cfb', verbose_name='\u81ea\u52a8\u5ba1\u6838\u5bf9\u5e94\u5173\u7cfb\u76d1\u6d4b\u65f6\u95f4'),
        ),
        migrations.AddField(
            model_name='checksettings',
            name='auto_review_time',
            field=models.IntegerField(default=3, help_text='\u5355\u4f4d\uff1a\u5929\u6570, \u81ea\u52a8\u5ba1\u6838\u4e2d\uff0c\u76d1\u6d4b\u53d1\u4ef6\u4eba-\u6536\u4ef6\u4eba\u5bf9\u5e94\u5173\u7cfb\u7684\u65f6\u95f4', verbose_name='\u81ea\u52a8\u5ba1\u6838\u5bf9\u5e94\u5173\u7cfb\u76d1\u6d4b\u65f6\u95f4'),
        ),
    ]
