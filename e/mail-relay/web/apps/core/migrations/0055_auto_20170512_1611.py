# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0054_auto_20170411_1022'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='sale',
            field=models.ForeignKey(related_name='sale', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='tech',
            field=models.ForeignKey(related_name='tech', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
