# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0013_auto_20151104_1154'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachmentBlacklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u5bf9\u9644\u4ef6\u8fdb\u884c\u68c0\u6d4b\uff0c\u5982\u679c\u9644\u4ef6\u540d\u79f0\u5305\u542b\u9ed1\u540d\u5355\u5173\u952e\u8bcd,\u3000\u5219\u5c06\u90ae\u4ef6\u6807\u5fd7\u4e3a\u9ad8\u5371\u90ae\u4ef6\u5ba1\u6838\u3002\u652f\u6301\u6b63\u5219', max_length=50, verbose_name='\u9644\u4ef6\u5173\u952e\u5b57')),
                ('relay', models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4e2d\u7ee7')),
                ('collect', models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4ee3\u6536')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
    ]
