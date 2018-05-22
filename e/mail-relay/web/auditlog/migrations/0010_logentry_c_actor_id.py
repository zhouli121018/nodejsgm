# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auditlog', '0009_logentry_relate_content_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='logentry',
            name='c_actor_id',
            field=models.BigIntegerField(db_index=True, null=True, verbose_name='customer actoer id', blank=True),
        ),
    ]
