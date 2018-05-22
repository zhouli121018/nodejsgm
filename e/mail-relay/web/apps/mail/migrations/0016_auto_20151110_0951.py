# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0015_attachmentblacklist_disabled'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailStateLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.CharField(max_length=20, verbose_name='\u65e5\u671f')),
                ('mail_id', models.IntegerField()),
                ('old_state', models.CharField(default=b'check', max_length=20, verbose_name='\u65e7\u72b6\u6001', choices=[(b'', b'--'), (b'check', '\u7b49\u5f85\u68c0\u6d4b'), (b'review', '\u7b49\u5f85\u5ba1\u6838'), (b'dispatch', '\u7b49\u5f85\u5206\u914dIP'), (b'send', '\u7b49\u5f85\u53d1\u9001'), (b'reject', '\u62d2\u7edd'), (b'retry', '\u7b49\u5f85\u91cd\u8bd5'), (b'bounce', '\u7b49\u5f85\u9000\u4fe1'), (b'finished', '\u5b8c\u6210')])),
                ('new_state', models.CharField(default=b'check', max_length=20, verbose_name='\u65b0\u72b6\u6001', choices=[(b'', b'--'), (b'check', '\u7b49\u5f85\u68c0\u6d4b'), (b'review', '\u7b49\u5f85\u5ba1\u6838'), (b'dispatch', '\u7b49\u5f85\u5206\u914dIP'), (b'send', '\u7b49\u5f85\u53d1\u9001'), (b'reject', '\u62d2\u7edd'), (b'retry', '\u7b49\u5f85\u91cd\u8bd5'), (b'bounce', '\u7b49\u5f85\u9000\u4fe1'), (b'finished', '\u5b8c\u6210')])),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
        migrations.AlterIndexTogether(
            name='mailstatelog',
            index_together=set([('date', 'mail_id')]),
        ),
    ]
