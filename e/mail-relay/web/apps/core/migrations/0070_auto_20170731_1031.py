# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0069_auto_20170731_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='ip',
            field=models.CharField(unique=True, max_length=100, verbose_name='SMTP\u4e3b\u673aIP'),
        ),
    ]
