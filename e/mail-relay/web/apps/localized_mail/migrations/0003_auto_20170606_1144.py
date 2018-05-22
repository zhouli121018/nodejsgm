# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('localized_mail', '0002_localizedmail_mail_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='localizedmail',
            name='check_result',
            field=models.CharField(choices=[(b'', b'--'), (b'high_risk', '\u9ad8\u5371\u90ae\u4ef6'), (b'sender_blacklist', '\u53d1\u4ef6\u9ed1'), (b'keyword_blacklist', '\u5185\u5bb9\u9ed1'), (b'subject_blacklist', '\u4e3b\u9898\u9ed1'), (b'subject_and_keyword', '\u4e3b\u9898\u548c\u5185\u5bb9\u5173\u952e\u5b57'), (b'cyber_spam', 'CYBER-Spam'), (b'spamassassin', '\u5783\u90ae(spamassassin)'), (b'error', '\u68c0\u6d4b\u51fa\u9519'), (b'c_sender_blacklist', '\u53d1\u4ef6\u4eba\u9ed1\u540d\u5355')], max_length=20, blank=True, null=True, verbose_name='\u68c0\u6d4b\u7ed3\u679c', db_index=True),
        ),
        migrations.AlterField(
            model_name='localizedmail',
            name='state',
            field=models.CharField(default=b'review', max_length=20, verbose_name='\u72b6\u6001', db_index=True, choices=[(b'', b'--'), (b'review', '\u7b49\u5f85\u5ba1\u6838'), (b'pass', '\u5ba1\u6838\u5df2\u901a\u8fc7'), (b'reject', '\u5ba1\u6838\u5df2\u62d2\u7edd'), (b'passing', '\u5ba1\u6838\u901a\u8fc7\u4e2d'), (b'rejecting', '\u5ba1\u6838\u62d2\u7edd\u4e2d')]),
        ),
    ]
