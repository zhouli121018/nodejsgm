# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20151103_1518'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bounce', models.BooleanField(default=True, verbose_name='\u5f00\u59cb\u9000\u4fe1')),
                ('customer', models.ForeignKey(to='core.Customer')),
            ],
        ),
    ]
