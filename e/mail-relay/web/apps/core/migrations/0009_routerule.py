# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20150924_0927'),
    ]

    operations = [
        migrations.CreateModel(
            name='RouteRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default=b'domain', max_length=b'10', verbose_name='\u7c7b\u578b', choices=[(b'domain', '\u76ee\u6807\u57df\u540d'), (b'keyword', '\u5173\u952e\u5b57')])),
                ('domain', models.CharField(help_text='\u4e00\u4e2a\u6216\u591a\u4e2a\u76ee\u6807\u57df\u540d\u7684\u90ae\u4ef6\u4ece\u67d0\u4e2a\u5730\u5740\u6c60\u53d1\u9001', max_length=100, verbose_name='\u76ee\u6807\u57df\u540d')),
                ('keyword', models.CharField(help_text='\u65e5\u5fd7\u4e2d\u542b\u6709\u67d0\u4e9b\u5173\u952e\u8bcd\u7684\u90ae\u4ef6\uff08\u5730\u5740\u6c60\u5168\u90e8IP\u53d1\u9001\u51fa\u9519\uff09\u4ece\u67d0\u4e2a\u5730\u5740\u6c60\u53d1\u9001', max_length=100, verbose_name='\u5173\u952e\u5b57')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528', choices=[(True, '\u662f'), (False, '\u5426')])),
                ('ip_pool', models.ForeignKey(verbose_name='\u53d1\u9001\u6c60', blank=True, to='core.IpPool', null=True)),
            ],
        ),
    ]
