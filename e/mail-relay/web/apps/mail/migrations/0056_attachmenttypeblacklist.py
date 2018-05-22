# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mail', '0055_remove_settings_max_same_subject'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachmentTypeBlacklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u7f51\u5173\u5c0f\u5371\u9644\u4ef6\u7c7b\u578b\uff0c\u5c0f\u5371\u9644\u4ef6\uff1a\u81ea\u52a8\u5220\u9664 \u975e\u4e2d\u6587 \u90ae\u4ef6\u4e2d xxx \u9644\u4ef6\u7c7b\u578b \u4e14 \u5c0f\u4e8eXXX KB\u7684\u90ae\u4ef6\uff0c\u76f4\u63a5\u5220\u9664\uff0c\u4e0d\u5ba1\u6838\uff0c\u4e0d\u5b66\u4e60\u3002\u8fc7\u6ee4\u987a\u5e8f\u5728 \u53d1\u4ef6\u4eba\u767d\u540d\u5355\u68c0\u6d4b \u4e4b\u540e\u3002 ', max_length=50, verbose_name='\u5c0f\u5371\u9644\u4ef6\u7c7b\u578b')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('operate_time', models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True)),
                ('creater', models.ForeignKey(related_name='attach_type_creater', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('operater', models.ForeignKey(related_name='attach_type_operater', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
