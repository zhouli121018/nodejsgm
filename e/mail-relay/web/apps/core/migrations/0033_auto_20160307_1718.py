# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0032_auto_20160127_1437'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=50, null=True, verbose_name='\u901a\u77e5\u4e3b\u9898')),
                ('content', models.TextField(verbose_name='\u901a\u77e5\u5185\u5bb9')),
                ('type', models.CharField(max_length=10, verbose_name='\u901a\u77e5\u7c7b\u578b', choices=[(b'', '\u65e0'), (b'bulk', '\u7fa4\u53d1\u90ae\u4ef6\u901a\u77e5'), (b'review', '\u5ba1\u6838\u90ae\u4ef6\u901a\u77e5')])),
                ('is_read', models.BooleanField(default=False, help_text='\u901a\u77e5\u662f\u5426\u9605\u8bfb', verbose_name='\u662f\u5426\u9605\u8bfb')),
                ('is_notice', models.BooleanField(default=False, verbose_name='\u662f\u5426\u53d1\u7ad9\u5185\u901a\u77e5')),
                ('is_sms', models.BooleanField(default=False, verbose_name='\u662f\u5426\u53d1\u77ed\u4fe1\u901a\u77e5')),
                ('is_email', models.BooleanField(default=False, verbose_name='\u662f\u5426\u53d1\u90ae\u4ef6\u901a\u77e5')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
        migrations.AlterField(
            model_name='customer',
            name='status',
            field=models.CharField(default=b'normal', max_length=10, verbose_name='\u72b6\u6001', choices=[(b'', '--'), (b'normal', '\u6b63\u5e38'), (b'expiring', '\u5373\u5c06\u8fc7\u671f'), (b'expired', '\u5df2\u8fc7\u671f'), (b'disabled', '\u5df2\u7981\u7528')]),
        ),
        migrations.AddField(
            model_name='notification',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Customer', help_text='\u901a\u77e5\u7684\u5ba2\u6237\u5bf9\u8c61', null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, help_text='\u901a\u77e5\u7684\u7ba1\u7406\u5458\u5bf9\u8c61', null=True),
        ),
    ]
