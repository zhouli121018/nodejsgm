# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0096_collectrecipientwhitelist_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='spamrptsettings',
            name='m_html_content',
            field=models.TextField(default='', help_text='\u5c06\u5783\u573e\u90ae\u4ef6\u9694\u79bb\u62a5\u544a\u53d1\u9001\u7ed9\u7f51\u5173\u7ba1\u7406\u5458, \u652f\u6301\u53d8\u91cf: {mail_from}\u8868\u793a\u53d1\u4ef6\u4eba, \u76f8\u5e94\u5b57\u6bb5\u4fe1\u606f\u8bf7\u67e5\u770b\u5907\u6ce8\u680f\u3002', verbose_name='\u5783\u573e\u90ae\u4ef6\u9694\u79bb\u62a5\u544a\u6a21\u677f(\u5bf9\u7ba1\u7406\u5458)'),
            preserve_default=False,
        ),
    ]
