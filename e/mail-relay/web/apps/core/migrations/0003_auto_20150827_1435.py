# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150825_0945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ippool',
            name='type',
            field=models.CharField(max_length=10, verbose_name='\u53d1\u9001\u6c60\u7c7b\u578b', choices=[(b'auto', '\u81ea\u52a8\u6c60'), (b'backup', '\u5907\u4efd\u6c60'), (b'manual', '\u624b\u52a8\u6c60')]),
        ),
    ]
