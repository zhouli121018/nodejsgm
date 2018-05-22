# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0066_auto_20170622_1048'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mail', '0103_auto_20170707_0935'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpamRptBlacklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('recipient', models.CharField(help_text='\u9694\u79bb\u62a5\u544a\u6536\u4ef6\u4eba\u9ed1\u540d\u5355:\u5982\u679c\u6536\u4ef6\u4eba\u5728\u9ed1\u540d\u5355\u4e2d\uff0c\u5219\u9694\u79bb\u62a5\u544a\u4e0d\u53d1\u9001\u7ed9\u8be5\u53d1\u4ef6\u4eba', max_length=150, verbose_name='\u6536\u4ef6\u4eba')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('operate_time', models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True)),
                ('creater', models.ForeignKey(related_name='spam_rpt_blacklist_creater', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to='core.Customer', null=True)),
                ('operater', models.ForeignKey(related_name='spam_rpt_blacklist_operater', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
