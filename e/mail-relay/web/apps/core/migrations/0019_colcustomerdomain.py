# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20151126_1508'),
    ]

    operations = [
        migrations.CreateModel(
            name='ColCustomerDomain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=100, verbose_name='\u5ba2\u6237\u57df\u540d')),
                ('forward_address', models.CharField(max_length=100, verbose_name='\u8f6c\u53d1\u5730\u5740')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('customer', models.ForeignKey(related_name='col_domain', to='core.Customer')),
            ],
        ),
    ]
