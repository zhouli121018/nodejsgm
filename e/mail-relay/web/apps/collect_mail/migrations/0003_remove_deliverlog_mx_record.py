# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collect_mail', '0002_highriskflag'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliverlog',
            name='mx_record',
        ),
    ]
