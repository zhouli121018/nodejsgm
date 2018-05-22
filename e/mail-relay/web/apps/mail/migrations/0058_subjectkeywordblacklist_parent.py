# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0057_auto_20160331_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjectkeywordblacklist',
            name='parent',
            field=models.ForeignKey(related_name='children', blank=True, to='mail.SubjectKeywordBlacklist', null=True),
        ),
    ]
