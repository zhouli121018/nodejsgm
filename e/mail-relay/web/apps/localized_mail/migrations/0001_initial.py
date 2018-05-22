# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0063_auto_20170527_1537'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocalizedMail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('check_result', models.CharField(choices=[(b'', b'--'), (b'error_format', '\u683c\u5f0f\u9519\u8bef'), (b'invalid_mail', '\u65e0\u6548\u5730\u5740'), (b'recipient_blacklist', '\u6536\u4ef6\u4eba\u9ed1\u540d\u5355'), (b'recipient_whitelist', '\u6536\u4ef6\u4eba\u767d\u540d\u5355'), (b'domain_blacklist', '\u57df\u540d\u9ed1\u540d\u5355'), (b'active_spam', '\u52a8\u6001SPAM'), (b'high_risk', '\u9ad8\u5371\u90ae\u4ef6'), (b'high_sender', '\u9ad8\u5371\u53d1\u4ef6\u4eba'), (b'sender_blacklist', '\u53d1\u4ef6\u9ed1'), (b'keyword_blacklist', '\u5185\u5bb9\u9ed1'), (b'subject_blacklist', '\u4e3b\u9898\u9ed1'), (b'custom_blacklist', '\u81ea\u52a8\u56de\u590d'), (b'subject_and_keyword', '\u4e3b\u9898\u548c\u5185\u5bb9\u5173\u952e\u5b57'), (b'bulk_email', '\u7fa4\u53d1\u90ae\u4ef6(\u9891\u7387)'), (b'bulk_email_subject', '\u7fa4\u53d1\u90ae\u4ef6(\u4e3b\u9898)'), (b'big_email', '\u5927\u90ae\u4ef6'), (b'innocent', '\u6b63\u5e38\u90ae\u4ef6'), (b'spam', '\u5783\u573e\u90ae\u4ef6(dspam)'), (b'cyber_spam', 'CYBER-Spam'), (b'spamassassin', '\u5783\u90ae(spamassassin)'), (b'virus', '\u75c5\u6bd2'), (b'auto_reject', '\u81ea\u52a8\u5ba1\u6838-\u62d2\u7edd'), (b'k_auto_reject', '\u5173\u952e\u5b57\u514d\u5ba1-\u62d2\u7edd'), (b'auto_pass', '\u81ea\u52a8\u5ba1\u6838-\u901a\u8fc7'), (b'error', '\u68c0\u6d4b\u51fa\u9519'), (b'auto_reject_attach', '\u81ea\u52a8\u62d2\u7edd-\u5c0f\u5371\u9644\u4ef6'), (b'esets', 'Esets \u75c5\u6bd2'), (b'sender_whitelist', '\u53d1\u4ef6\u4eba\u767d\u540d\u5355')], max_length=20, blank=True, null=True, verbose_name='\u68c0\u6d4b\u7ed3\u679c', db_index=True)),
                ('check_message', models.TextField(null=True, verbose_name='\u68c0\u6d4b\u8be6\u7ec6\u7ed3\u679c', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('mail_from', models.CharField(max_length=150, null=True, verbose_name='\u53d1\u4ef6\u4eba', blank=True)),
                ('mail_to', models.CharField(max_length=150, null=True, verbose_name='\u6536\u4ef6\u4eba', blank=True)),
                ('subject', models.CharField(max_length=800, null=True, verbose_name='\u4e3b\u9898', blank=True)),
                ('state', models.CharField(default=b'review', max_length=20, verbose_name='\u72b6\u6001', db_index=True, choices=[(b'', b'--'), (b'review', '\u7b49\u5f85\u5ba1\u6838'), (b'pass', '\u5ba1\u6838\u901a\u8fc7'), (b'reject', '\u5ba1\u6838\u62d2\u7edd')])),
                ('size', models.IntegerField(default=0, verbose_name='\u90ae\u4ef6\u5927\u5c0f')),
                ('review_time', models.DateTimeField(null=True, verbose_name='\u5ba1\u6838\u65f6\u95f4', blank=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to='core.Customer', null=True)),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
