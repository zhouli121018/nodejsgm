# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0073_keywordblacklist_is_regex'),
    ]

    operations = [
        migrations.AddField(
            model_name='customkeywordblacklist',
            name='is_regex',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u652f\u6301\u6b63\u5219'),
        ),
    ]
