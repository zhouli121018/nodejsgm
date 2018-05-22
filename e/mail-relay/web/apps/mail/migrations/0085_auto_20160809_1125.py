# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0084_auto_20160809_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sendercreditlog',
            name='reason',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='\u539f\u56e0', choices=[(b'check_auto_reject', '\u514d\u5ba1\u62d2\u7edd'), (b'check_dspam', 'Dspam'), (b'send_spam', '\u53d1\u9001\u5783\u573e\u90ae\u4ef6'), (b'send_not_exist', '\u53d1\u9001\u4e0d\u5b58\u5728\u90ae\u4ef6'), (b'review_reject', '\u5ba1\u6838\u62d2\u7edd'), (b'review_pass', '\u5ba1\u6838\u901a\u8fc7')]),
        ),
    ]
