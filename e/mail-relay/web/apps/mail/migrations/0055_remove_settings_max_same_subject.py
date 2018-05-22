# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0054_settings_invalid_mail_expire_days'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='settings',
            name='max_same_subject',
        ),
    ]
