# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0086_relaysenderwhitelist'),
    ]

    operations = [
        migrations.AddField(
            model_name='checksettings',
            name='credit',
            field=models.IntegerField(default=1000, help_text='\u68c0\u6d4b\u4e2d\u7ee7\u6536\u4ef6\u4eba\u767d\u540d\u5355\u65f6\uff0c\u8981\u6c42 \u53d1\u4ef6\u4eba\u4fe1\u8a89\u5ea6 \u9ad8\u4e8e\u6b64\u8bbe\u7f6e\u503c', verbose_name='\u53d1\u4ef6\u4eba\u4fe1\u8a89\u5ea6\u68c0\u6d4b\u503c'),
        ),
    ]
