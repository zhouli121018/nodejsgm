# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collect_mail', '0013_auto_20170522_0940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailstatelog',
            name='new_state',
            field=models.CharField(default=b'check', max_length=20, verbose_name='\u65b0\u72b6\u6001', choices=[(b'', b'--'), (b'check', '\u7b49\u5f85\u68c0\u6d4b'), (b'review', '\u7b49\u5f85\u5ba1\u6838'), (b'send', '\u7b49\u5f85\u53d1\u9001'), (b'reject', '\u62d2\u7edd'), (b'retry', '\u7b49\u5f85\u91cd\u8bd5'), (b'bounce', '\u7b49\u5f85\u9000\u4fe1'), (b'finished', '\u5b8c\u6210'), (b'fail_finished', '\u5b8c\u6210(\u5931\u8d25)')]),
        ),
        migrations.AlterField(
            model_name='mailstatelog',
            name='old_state',
            field=models.CharField(default=b'check', max_length=20, verbose_name='\u65e7\u72b6\u6001', choices=[(b'', b'--'), (b'check', '\u7b49\u5f85\u68c0\u6d4b'), (b'review', '\u7b49\u5f85\u5ba1\u6838'), (b'send', '\u7b49\u5f85\u53d1\u9001'), (b'reject', '\u62d2\u7edd'), (b'retry', '\u7b49\u5f85\u91cd\u8bd5'), (b'bounce', '\u7b49\u5f85\u9000\u4fe1'), (b'finished', '\u5b8c\u6210'), (b'fail_finished', '\u5b8c\u6210(\u5931\u8d25)')]),
        ),
    ]
