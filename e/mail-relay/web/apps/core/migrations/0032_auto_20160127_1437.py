# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0031_auto_20160119_0854'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='creater',
            field=models.ForeignKey(related_name='creater22', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='operater',
            field=models.ForeignKey(related_name='operater22', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
