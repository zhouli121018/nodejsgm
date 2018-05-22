# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0058_subjectkeywordblacklist_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjectkeywordblacklist',
            name='parent',
            field=models.ForeignKey(related_name='children', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='mail.SubjectKeywordBlacklist', null=True),
        ),
    ]
