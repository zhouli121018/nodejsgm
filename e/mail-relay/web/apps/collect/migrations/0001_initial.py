# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ColCustomer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=50, verbose_name='\u5ba2\u6237\u5e10\u53f7')),
                ('password', models.CharField(max_length=128, null=True, verbose_name='\u5bc6\u7801', blank=True)),
                ('company', models.CharField(unique=True, max_length=100, verbose_name='\u516c\u53f8\u540d\u79f0')),
                ('service_start', models.DateField(verbose_name='\u670d\u52a1\u5f00\u59cb\u65f6\u95f4')),
                ('service_end', models.DateField(verbose_name='\u670d\u52a1\u5230\u671f\u65f6\u95f4')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('status', models.CharField(default=b'normal', max_length=10, verbose_name='\u72b6\u6001', choices=[(b'', '--'), (b'normal', '\u6b63\u5e38'), (b'expired', '\u8fc7\u671f'), (b'disabled', '\u7981\u7528')])),
            ],
        ),
        migrations.CreateModel(
            name='ColCustomerDomain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=100, verbose_name='\u5ba2\u6237\u4fe1\u4efb\u53d1\u9001\u57df\u540d')),
                ('ip', models.GenericIPAddressField(verbose_name='\u5ba2\u6237\u57df\u540d\u5bf9\u5e94ip')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('customer', models.ForeignKey(related_name='domain', to='collect.ColCustomer')),
            ],
        ),
        migrations.CreateModel(
            name='ColCustomerSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('check_subject', models.BooleanField(default=True, verbose_name='\u4e3b\u9898\u5173\u952e\u5b57\u8fc7\u6ee4')),
                ('check_content', models.BooleanField(default=True, verbose_name='\u5185\u5bb9\u5173\u952e\u5b57\u8fc7\u6ee4')),
                ('check_dspam', models.BooleanField(default=True, verbose_name='dspam\u8fc7\u6ee4')),
                ('check_spam', models.BooleanField(default=True, verbose_name='spamassassion\u8fc7\u6ee4')),
                ('check_high_risk', models.BooleanField(default=True, verbose_name='\u9ad8\u5371\u90ae\u4ef6\u8fc7\u6ee4')),
                ('customer', models.ForeignKey(related_name='setting', to='collect.ColCustomer')),
            ],
        ),
    ]
