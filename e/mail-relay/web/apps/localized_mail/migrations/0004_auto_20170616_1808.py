# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('localized_mail', '0003_auto_20170606_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='localizedmail',
            name='created_date',
            field=models.DateField(default=datetime.datetime(2017, 6, 16, 10, 8, 35, 342273, tzinfo=utc), auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f', db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='localizedmail',
            name='origin',
            field=models.CharField(default=b'collect', max_length=20, verbose_name='\u6765\u6e90', db_index=True, choices=[(b'collect', '\u7f51\u5173'), (b'relay', '\u4e2d\u7ee7')]),
        ),
    ]
