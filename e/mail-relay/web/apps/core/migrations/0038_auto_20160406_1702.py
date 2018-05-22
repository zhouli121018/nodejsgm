# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_auto_20160330_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='manager',
            field=models.ForeignKey(related_name='notification_manager', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, help_text='\u901a\u77e5\u7684\u7ba1\u7406\u5458\u5bf9\u8c61', null=True),
        ),
    ]
