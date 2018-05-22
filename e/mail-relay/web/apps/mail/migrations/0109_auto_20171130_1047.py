# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0108_auto_20171130_1004'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='relaysenderwhitelist',
            options={'verbose_name': '\u4e2d\u7ee7\u53d1\u4ef6\u4eba\u767d\u540d\u5355'},
        ),
        migrations.AlterModelOptions(
            name='spamrptblacklist',
            options={'verbose_name': '\u7f51\u5173\u9694\u79bb\u62a5\u544a\u6536\u4ef6\u4eba\u9ed1\u540d\u5355'},
        ),
    ]
