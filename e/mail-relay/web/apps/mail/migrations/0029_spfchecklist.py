# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0028_auto_20151224_1554'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpfChecklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(help_text='\u5f3a\u5236SPF\u68c0\u67e5\u57df\u540d\u5e93\uff0c\u5728\u6b64\u5e93\u4e2d\u7684\u57df\u540d\u5f3a\u5236\u68c0\u67e5SPF\uff0c\u4e0d\u8bba\u5ba2\u6237\u662f\u5426\u5f00\u542fSPF\u529f\u80fd. \u4e0d\u652f\u6301\u6b63\u5219, \u683c\u5f0f\u5982\uff1atest.com  ,\u5305\u542b\u6240\u6709test.com\u7ed3\u5c3e\u7684\u57df\u540d', max_length=100, verbose_name='\u57df\u540d')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
    ]
