# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_auto_20160127_1437'),
        ('mail', '0038_auto_20160202_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='big_email',
            field=models.IntegerField(default=20, help_text='\u5355\u4f4d\uff1aMB\uff0c\u5927\u4e8eXXX kb\u7684\u90ae\u4ef6\u4ece\u5927\u90ae\u4ef6\u5730\u5740\u6c60\u53d1\uff0c\u5982\u679c\u53d1\u9001\u5931\u8d25\uff0c\u518d\u4ece\u4e4b\u524d\u7684\u901a\u9053\u53d1', verbose_name='\u4f20\u8f93\u5927\u90ae\u4ef6\u9600\u503c'),
        ),
        migrations.AddField(
            model_name='settings',
            name='big_email_pool',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.IpPool', help_text='\u5927\u90ae\u4ef6\u53d1\u9001\u6c60', null=True),
        ),
    ]
