# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0067_customersetting_service_notice'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoreLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u64cd\u4f5c\u65f6\u95f4')),
                ('action', models.CharField(choices=[(b'user_login', '\u767b\u5f55\u65e5\u5fd7')], max_length=20, blank=True, null=True, verbose_name='\u64cd\u4f5c\u7c7b\u578b', db_index=True)),
                ('desc', models.TextField(verbose_name='\u8bf4\u660e')),
                ('ip', models.CharField(max_length=15, null=True, verbose_name='\u64cd\u4f5cIP', blank=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to='core.Customer', null=True)),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
