# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('localized_mail', '0004_auto_20170616_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='localizedmail',
            name='origin',
            field=models.CharField(default=b'collect', max_length=20, verbose_name='\u6765\u6e90', db_index=True, choices=[(b'', b'--'), (b'collect', '\u7f51\u5173'), (b'relay', '\u4e2d\u7ee7')]),
        ),
    ]
