# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0047_urlremark'),
    ]

    operations = [
        migrations.AddField(
            model_name='urlremark',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 8, 2, 9, 29, 29, 947688, tzinfo=utc), verbose_name='\u521b\u5efa\u65e5\u671f', auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='urlremark',
            name='create_uid',
            field=models.ForeignKey(related_name='urlremark_user1', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='urlremark',
            name='write_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 8, 2, 9, 29, 37, 675528, tzinfo=utc), verbose_name='\u66f4\u65b0\u65f6\u95f4', auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='urlremark',
            name='write_uid',
            field=models.ForeignKey(related_name='urlremark_user2', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
