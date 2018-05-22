# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('collect_mail', '0012_statistics_error_type_8'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewstatistics',
            name='reviewer',
            field=models.ForeignKey(related_name='collect_review_statistics', on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='customer',
            field=models.ForeignKey(related_name='collect_statistics', on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to='core.Customer', null=True),
        ),
    ]
