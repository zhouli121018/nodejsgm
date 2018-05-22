# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20150827_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='status',
            field=models.CharField(default=b'normal', max_length=10, verbose_name='\u72b6\u6001', choices=[(b'normal', '\u6b63\u5e38'), (b'expired', '\u8fc7\u671f'), (b'disabled', '\u7981\u7528')]),
        ),
    ]
