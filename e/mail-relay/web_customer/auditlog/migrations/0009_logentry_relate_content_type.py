# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auditlog', '0008_logentry_relate_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='logentry',
            name='relate_content_type',
            field=models.ForeignKey(related_name='relate+', verbose_name='relate content type', blank=True, to='contenttypes.ContentType', null=True),
        ),
    ]
