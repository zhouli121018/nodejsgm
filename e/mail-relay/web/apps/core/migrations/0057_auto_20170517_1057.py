# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0056_customer_service'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(max_length=10, verbose_name='\u901a\u77e5\u7c7b\u578b', choices=[(b'', '\u65e0'), (b'bulk', '\u8fdd\u89c4\u90ae\u4ef6\u901a\u77e5'), (b'review', '\u5ba1\u6838\u90ae\u4ef6\u901a\u77e5'), (b'ip', '\u53d1\u9001\u673aIP\u4e0d\u901a\u901a\u77e5'), (b'jam', '\u670d\u52a1\u5668\u62e5\u5835\u901a\u77e5'), (b'collect', '\u7f51\u5173\u7528\u6237\u8d85\u8fc7\u9650\u5236\u901a\u77e5'), (b'relay', '\u4e2d\u7ee7\u7528\u6237\u8d85\u8fc7\u9650\u5236\u901a\u77e5'), (b'c_service', '\u7f51\u5173\u670d\u52a1\u5230\u671f\u63d0\u9192'), (b'r_service', '\u4e2d\u7ee7\u670d\u52a1\u5230\u671f\u63d0\u9192')]),
        ),
    ]
