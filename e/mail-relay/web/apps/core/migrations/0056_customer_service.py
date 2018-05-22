# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0055_auto_20170512_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='service',
            field=models.ForeignKey(related_name='service', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
