# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0104_spamrptblacklist'),
    ]

    operations = [
        migrations.AddField(
            model_name='noticesettings',
            name='c_deliver_exception_content',
            field=models.TextField(default='', help_text='\u7f51\u5173\u5ba2\u6237\u670d\u52a1\u5668DOWN\u673a\u63d0\u9192\u7ba1\u7406\u5458\u548c\u5ba2\u6237\u7ba1\u7406\u5458, {customer}\u5ba2\u6237\u540d\u79f0, {domain}\u5ba2\u6237\u57df\u540d, {ip}\u5ba2\u6237IP', verbose_name='\u7f51\u5173\u5ba2\u6237\u670d\u52a1\u5668DOWN\u673a\u901a\u77e5'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='noticesettings',
            name='c_deliver_exception_interval',
            field=models.IntegerField(default=60, help_text='\u5355\u4f4d\uff1a\u5206\u949f, \u901a\u77e5\u53d1\u9001\u95f4\u9694', verbose_name='\u7f51\u5173\u5ba2\u6237\u670d\u52a1\u5668DOWN\u673a\u901a\u77e5\u95f4\u9694'),
        ),
    ]
