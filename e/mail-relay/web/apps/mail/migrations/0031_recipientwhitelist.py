# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0030_tempsenderblacklist'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipientWhitelist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u51e1\u662f\u6536\u4ef6\u4eba\u57df\u540d\u5728\u767d\u540d\u5355\u4e2d\uff0c\u53ea\u505aDSPAM\u8fc7\u6ee4\uff0c\u7136\u540e\u5c31\u76f4\u63a5\u53d1\u9001', max_length=50, verbose_name='\u4e2d\u7ee7\u6536\u4ef6\u4eba\u57df\u540d\u767d\u540d\u5355')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('hits', models.IntegerField(default=0, verbose_name='\u547d\u4e2d\u6b21\u6570')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
    ]
