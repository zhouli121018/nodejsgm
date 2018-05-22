# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collect_mail', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HighRiskFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u9ad8\u5371\u9644\u4ef6\u6807\u5fd7, \u5bf9\u9644\u4ef6\u8fdb\u884c\u76d1\u63a7\uff0c\u9644\u4ef6\u7684\u7c7b\u578b\u53ef\u5b9a\u4e49\uff0c\u6bd4\u5982js\u3001vbs\u7b49\u3002\u542b\u6709\u6b64\u7c7b\u9644\u4ef6\u7684\u90ae\u4ef6\u653e\u5165\u9ad8\u5371\u90ae\u4ef6\u5ba1\u6838\u3002', max_length=50, verbose_name='\u9ad8\u5371\u9644\u4ef6\u6807\u5fd7')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
    ]
