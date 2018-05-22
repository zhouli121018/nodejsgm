# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0033_auto_20160307_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='manager',
            field=models.ForeignKey(related_name='c_manager', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='support_email',
            field=models.CharField(max_length=50, null=True, verbose_name='\u5ba2\u6237\u652f\u6301\u90ae\u7bb1', blank=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.EmailField(max_length=50, null=True, verbose_name='\u90ae\u7bb1', blank=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(max_length=10, verbose_name='\u901a\u77e5\u7c7b\u578b', choices=[(b'', '\u65e0'), (b'bulk', '\u7fa4\u53d1\u90ae\u4ef6\u901a\u77e5'), (b'review', '\u5ba1\u6838\u90ae\u4ef6\u901a\u77e5'), (b'ip', '\u53d1\u9001\u673aIP\u4e0d\u901a\u901a\u77e5')]),
        ),
    ]
