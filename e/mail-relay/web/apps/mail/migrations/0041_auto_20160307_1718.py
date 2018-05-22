# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mail', '0040_auto_20160224_1038'),
    ]

    operations = [
        migrations.CreateModel(
            name='NoticeSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bulk_content', models.TextField(help_text='\u7528\u6237\u7fa4\u53d1\u90ae\u4ef6\u7684\u65f6\u5019\u901a\u77e5\u5ba2\u6237\u548c\u5bf9\u5e94\u7684\u6280\u672f\u652f\u6301', verbose_name='\u7fa4\u53d1\u90ae\u4ef6\u901a\u77e5')),
                ('bulk_interval', models.IntegerField(default=60, help_text='\u5355\u4f4d\uff1a\u5206\u949f\uff0c\u7fa4\u53d1\u901a\u77e5\u53d1\u9001\u95f4\u9694\u65f6\u95f4', verbose_name='\u7fa4\u53d1\u901a\u77e5\u95f4\u9694')),
                ('review_content', models.TextField(help_text='\u9700\u5ba1\u6838\u7684\u90ae\u4ef6\u8d85\u8fc7XXX\u5c01\uff08\u4e2d\u7ee7+\u7f51\u5173-cyber\uff09\u53d1\u9001\u901a\u77e5\u7ed9\u9ed8\u8ba4\u5ba1\u6838\u4eba\u5458,\u652f\u6301\u53d8\u91cf: {count}\u8868\u793a\u5ba1\u6838\u6570\u91cf', verbose_name='\u5ba1\u6838\u90ae\u4ef6\u901a\u77e5')),
                ('review_interval', models.IntegerField(default=15, help_text='\u5355\u4f4d\uff1a\u5206\u949f\uff0c\u7fa4\u53d1\u901a\u77e5\u53d1\u9001\u95f4\u9694\u65f6\u95f4', verbose_name='\u5ba1\u6838\u901a\u77e5\u95f4\u9694')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, help_text='\u9700\u901a\u77e5\u7684\u9ed8\u8ba4\u5ba1\u6838\u4eba\u5458', null=True, verbose_name='\u9ed8\u8ba4\u5ba1\u6838\u4eba\u5458')),
            ],
        ),
        migrations.AlterField(
            model_name='settings',
            name='big_email_pool',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.IpPool', help_text='\u5927\u90ae\u4ef6\u53d1\u9001\u6c60', null=True, verbose_name='\u5927\u90ae\u4ef6\u53d1\u9001\u6c60'),
        ),
    ]
