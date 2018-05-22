# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mail', '0037_reviewstatistics'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewstatistics',
            name='reviewer',
            field=models.ForeignKey(related_name='review_statistics', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='reviewstatistics',
            name='type',
            field=models.CharField(default=b'all', max_length=10, verbose_name='\u7c7b\u578b', choices=[(b'all', '\u5168\u90e8'), (b'reviewer', '\u5ba1\u6838\u5458')]),
        ),
    ]
