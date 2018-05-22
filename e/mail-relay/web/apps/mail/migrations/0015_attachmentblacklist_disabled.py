# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0014_attachmentblacklist'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachmentblacklist',
            name='disabled',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528'),
        ),
    ]
