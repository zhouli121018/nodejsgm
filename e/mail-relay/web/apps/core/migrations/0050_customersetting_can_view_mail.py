# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_customersetting_bigmail'),
    ]

    operations = [
        migrations.AddField(
            model_name='customersetting',
            name='can_view_mail',
            field=models.BooleanField(default=True, verbose_name='\u7f51\u5173\uff1a\u7528\u6237\u662f\u5426\u53ef\u4ee5\u67e5\u770b\u90ae\u4ef6'),
        ),
    ]
