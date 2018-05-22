# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0107_auto_20171025_1027'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attachmentblacklist',
            options={'ordering': ('order',), 'verbose_name': '\u9644\u4ef6\u5173\u952e\u5b57\u9ed1\u540d\u5355'},
        ),
        migrations.AlterModelOptions(
            name='attachmenttypeblacklist',
            options={'verbose_name': '\u7f51\u5173\u5c0f\u5371\u9644\u4ef6\u7c7b\u578b'},
        ),
        migrations.AlterModelOptions(
            name='collectrecipientchecklist',
            options={'verbose_name': '\u7f51\u5173\u6536\u4ef6\u4eba\u5f3a\u5236\u68c0\u6d4b\u540d\u5355'},
        ),
        migrations.AlterModelOptions(
            name='collectrecipientwhitelist',
            options={'verbose_name': '\u7f51\u5173\u6536\u4ef6\u4eba\u767d\u540d\u5355'},
        ),
        migrations.AlterModelOptions(
            name='customersenderblacklist',
            options={'verbose_name': '\u7f51\u5173\u53d1\u4ef6\u4eba\u9ed1\u540d\u5355'},
        ),
        migrations.AlterModelOptions(
            name='customkeywordblacklist',
            options={'verbose_name': '\u4e2d\u7ee7\u81ea\u52a8\u56de\u590d\u5173\u952e\u5b57'},
        ),
        migrations.AlterModelOptions(
            name='domainblacklist',
            options={'verbose_name': '\u4e2d\u7ee7\u53d1\u4ef6\u4eba\u57df\u540d\u9ed1\u540d\u5355'},
        ),
        migrations.AlterModelOptions(
            name='invalidsenderwhitelist',
            options={'verbose_name': '\u4e2d\u7ee7\u65e0\u6548\u5730\u5740\u767d\u540d\u5355'},
        ),
        migrations.AlterModelOptions(
            name='keywordblacklist',
            options={'ordering': ('order',), 'verbose_name': '\u5185\u5bb9\u5173\u952e\u5b57\u9ed1\u540d\u5355'},
        ),
        migrations.AlterModelOptions(
            name='recipientblacklist',
            options={'verbose_name': '\u6536\u4ef6\u4eba\u9ed1\u540d\u5355'},
        ),
        migrations.AlterModelOptions(
            name='recipientwhitelist',
            options={'verbose_name': '\u4e2d\u7ee7\u6536\u4ef6\u4eba\u767d\u540d\u5355'},
        ),
        migrations.AlterModelOptions(
            name='senderblacklist',
            options={'ordering': ('order',), 'verbose_name': '\u53d1\u4ef6\u4eba\u5173\u952e\u5b57\u9ed1\u540d\u5355'},
        ),
        migrations.AlterModelOptions(
            name='senderwhitelist',
            options={'verbose_name': '\u7f51\u5173\u53d1\u4ef6\u4eba\u767d\u540d\u5355'},
        ),
        migrations.AlterModelOptions(
            name='subjectkeywordblacklist',
            options={'ordering': ('order',), 'verbose_name': '\u4e3b\u9898\u5173\u952e\u5b57\u9ed1\u540d\u5355'},
        ),
        migrations.AlterModelOptions(
            name='subjectkeywordwhitelist',
            options={'verbose_name': '\u4e2d\u7ee7\u4e3b\u9898\u767d\u540d\u5355'},
        ),
        migrations.AlterModelOptions(
            name='tempsenderblacklist',
            options={'verbose_name': '\u4e2d\u7ee7\u4e34\u65f6\u53d1\u4ef6\u4eba\u9ed1\u540d\u5355'},
        ),
    ]
