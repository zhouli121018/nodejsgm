# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_auto_20160712_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersetting',
            name='spamrpt',
            field=models.BooleanField(default=False, help_text='\u9009\u4e2d\u65f6\u4e3a\u5f00\u542f,\u4f1a\u5c06\u88ab\u62d2\u7edd\u7684\u90ae\u4ef6\u4ee5\u62a5\u544a\u7684\u5f62\u5f0f\u53d1\u9001\u7ed9\u8be5\u7528\u6237,\u9ed8\u8ba4\u6bcf\u5929\u96f6\u70b9\u53d1\u4e0a\u4e00\u5929\u7684\u90ae\u4ef6\uff1b\u5f53\u5173\u95ed\u65f6\uff0c\u4e0d\u4f1a\u53d1\u9001\u88ab\u62d2\u7edd\u7684\u90ae\u4ef6\u7ed9\u7528\u6237', verbose_name='\u7f51\u5173\uff1a\u662f\u5426\u5f00\u542f\u5783\u573e\u90ae\u4ef6\u9694\u79bb\u62a5\u544a\u5f00\u5173'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(max_length=10, verbose_name='\u901a\u77e5\u7c7b\u578b', choices=[(b'', '\u65e0'), (b'bulk', '\u8fdd\u89c4\u90ae\u4ef6\u901a\u77e5'), (b'review', '\u5ba1\u6838\u90ae\u4ef6\u901a\u77e5'), (b'ip', '\u53d1\u9001\u673aIP\u4e0d\u901a\u901a\u77e5'), (b'jam', '\u670d\u52a1\u5668\u62e5\u5835\u901a\u77e5'), (b'collect', '\u7f51\u5173\u7528\u6237\u8d85\u8fc7\u9650\u5236\u901a\u77e5'), (b'relay', '\u4e2d\u7ee7\u7528\u6237\u8d85\u8fc7\u9650\u5236\u901a\u77e5')]),
        ),
    ]
