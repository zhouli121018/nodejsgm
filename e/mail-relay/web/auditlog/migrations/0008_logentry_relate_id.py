# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auditlog', '0007_object_pk_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='logentry',
            name='relate_id',
            field=models.BigIntegerField(db_index=True, null=True, verbose_name='relate object id', blank=True),
        ),
    ]
