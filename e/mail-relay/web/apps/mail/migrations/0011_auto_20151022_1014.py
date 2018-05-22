# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0010_auto_20151020_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='checksettings',
            name='auto_review_time_end',
            field=models.IntegerField(default=19, help_text='0-24\u4e4b\u5185\u7684\u6574\u6570\uff0c\u9ed8\u8ba4\u665a\u4e0a19\u70b9\uff0c\u81ea\u52a8\u5ba1\u6838\u5f00\u59cb\u5de5\u4f5c\u65f6\u95f4\uff0c \u53ea\u6709\u5728\u65e9\u4e0aX\u70b9\u5230\u665aX\u70b9 \u81ea\u52a8\u5ba1\u6838\u624d\u5de5\u4f5c', verbose_name='\u81ea\u52a8\u5ba1\u6838\u6709\u6548\u7ed3\u675f\u65f6\u95f4'),
        ),
        migrations.AddField(
            model_name='checksettings',
            name='auto_review_time_start',
            field=models.IntegerField(default=7, help_text='0-24\u4e4b\u5185\u7684\u6574\u6570\uff0c\u9ed8\u8ba4\u65e9\u4e0a7\u70b9\uff0c\u81ea\u52a8\u5ba1\u6838\u5f00\u59cb\u5de5\u4f5c\u65f6\u95f4\uff0c \u53ea\u6709\u5728\u65e9\u4e0aX\u70b9\u5230\u665aX\u70b9 \u81ea\u52a8\u5ba1\u6838\u624d\u5de5\u4f5c', verbose_name='\u81ea\u52a8\u5ba1\u6838\u6709\u6548\u5f00\u59cb\u65f6\u95f4'),
        ),
        migrations.AlterField(
            model_name='checksettings',
            name='auto_review_num',
            field=models.IntegerField(default=10, help_text='\u5355\u4f4d\uff1a\u64cd\u4f5c\u6b21\u6570, \u81ea\u52a8\u5ba1\u6838\u4e2d\uff0c\u53d1\u4ef6\u4eba-\u6536\u4ef6\u4eba\u8fde\u7eedX\u6b21\u901a\u8fc7/\u62d2\u7edd,\u5219\u8bb0\u5f55\u76f8\u5e94\u5173\u7cfb', verbose_name='\u81ea\u52a8\u5ba1\u6838\u64cd\u4f5c\u6b21\u6570'),
        ),
    ]
