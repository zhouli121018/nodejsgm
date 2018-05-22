# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0053_settings_max_same_subject'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='invalid_mail_expire_days',
            field=models.IntegerField(default=30, help_text='\u5355\u4f4d\uff1a\u5929\u6570\uff0c\u6dfb\u52a0\u65f6\u95f4\u8d85\u8fc7\u8be5\u5929\u6570\u7684\u65e0\u6548\u5730\u5740\u76f4\u63a5\u5220\u9664', verbose_name='\u65e0\u6548\u5730\u5740\u6709\u6548\u671f\u5929\u6570'),
        ),
    ]
