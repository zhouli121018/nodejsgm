# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0048_auto_20160802_1729'),
        ('mail', '0079_auto_20160725_0956'),
    ]

    operations = [
        migrations.CreateModel(
            name='SenderBlockedRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sender', models.CharField(max_length=100, verbose_name='\u53d1\u4ef6\u4eba')),
                ('blocked_days', models.IntegerField(default=0, verbose_name='\u88ab\u5c01\u5929\u6570')),
                ('opt_time', models.DateTimeField(auto_now_add=True, verbose_name='\u6dfb\u52a0\u65f6\u95f4')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Customer', null=True)),
                ('opter', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
