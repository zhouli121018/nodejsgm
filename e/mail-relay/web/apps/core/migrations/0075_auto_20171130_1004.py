# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0074_auto_20171018_1503'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='colcustomerdomain',
            options={'verbose_name': '\u7f51\u5173\u4fe1\u4efb\u57df\u540d'},
        ),
        migrations.AlterModelOptions(
            name='customer',
            options={'verbose_name': '\u5ba2\u6237\u4fe1\u606f'},
        ),
        migrations.AlterModelOptions(
            name='customerdomain',
            options={'verbose_name': '\u4e2d\u7ee7\u4fe1\u4efb\u57df\u540d'},
        ),
        migrations.AlterModelOptions(
            name='customerip',
            options={'verbose_name': '\u4e2d\u7ee7\u4fe1\u4efbIP'},
        ),
        migrations.AlterModelOptions(
            name='customermailbox',
            options={'verbose_name': '\u4e2d\u7ee7\u5e10\u53f7'},
        ),
    ]
