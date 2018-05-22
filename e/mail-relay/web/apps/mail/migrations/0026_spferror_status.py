# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0025_bulkcustomer_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='spferror',
            name='status',
            field=models.CharField(default=b'deal', max_length=10, verbose_name='\u72b6\u6001', choices=[(b'deal', '\u5f85\u5904\u7406'), (b'dealed', '\u5df2\u5904\u7406')]),
        ),
    ]
