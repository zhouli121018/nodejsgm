# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0064_auto_20160425_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulkcustomer',
            name='type',
            field=models.CharField(default=b'nomal', max_length=10, verbose_name='\u7c7b\u578b', choices=[(b'nomal', '\u6b63\u5e38\u7fa4\u53d1'), (b'evil', '\u6076\u610f\u7fa4\u53d1')]),
        ),
    ]
