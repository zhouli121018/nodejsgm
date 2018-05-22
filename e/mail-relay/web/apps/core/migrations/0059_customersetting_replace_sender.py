# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0058_customersetting_m_spamrpt'),
    ]

    operations = [
        migrations.AddField(
            model_name='customersetting',
            name='replace_sender',
            field=models.BooleanField(default=False, verbose_name='\u4e2d\u7ee7:\u662f\u5426\u66ff\u6362\u771f\u5b9e\u53d1\u4ef6\u4eba\uff0c\u5982\u679c\u5f00\u542f,\u81ea\u52a8\u628afrom\u5934\u6539\u6210\u771f\u5b9e\u7684\u53d1\u4ef6\u4eba'),
        ),
    ]
