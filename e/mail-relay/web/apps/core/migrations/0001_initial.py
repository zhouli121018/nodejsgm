# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='\u5982\uff1a\u7535\u4fe1-1', max_length=50, verbose_name='SMTP\u4e3b\u673a\u540d')),
                ('ip', models.GenericIPAddressField(help_text='\u5982\uff1a192.168.1.188', verbose_name='SMTP\u4e3b\u673aIP')),
                ('port', models.IntegerField(default=22, verbose_name='sshd\u7aef\u53e3')),
                ('api_url', models.URLField(help_text='\u9ed8\u8ba4\u4e3a\uff1ahttp://\u4e3b\u673aIP:10001/state/', max_length=150, null=True, verbose_name='API\u5730\u5740', blank=True)),
                ('description', models.TextField(null=True, verbose_name='\u63cf\u8ff0', blank=True)),
                ('username', models.CharField(max_length=50, verbose_name='\u7528\u6237\u540d')),
                ('password', models.CharField(help_text='\u5bc6\u7801\u5c06\u4f1a\u660e\u6587\u663e\u793a', max_length=100, verbose_name='\u5bc6\u7801')),
                ('deploy_status', models.CharField(default=b'normal', max_length=50, verbose_name='\u90e8\u7f72\u72b6\u6001', choices=[(b'normal', '\u6b63\u5e38'), (b'fail', '\u90e8\u7f72\u5931\u8d25'), (b'success', '\u90e8\u7f72\u6210\u529f'), (b'waiting', '\u7b49\u5f85\u90e8\u7f72'), (b'helo_waiting', 'helo\u7b49\u5f85\u90e8\u7f72'), (b'deploying', '\u90e8\u7f72\u4e2d'), (b'helo_deploying', 'helo\u90e8\u7f72\u4e2d')])),
                ('deploy_dtm', models.DateTimeField(null=True, verbose_name='\u6700\u8fd1\u90e8\u7f72\u65f6\u95f4')),
                ('deploy_info', models.TextField(max_length=2000, null=True, verbose_name='\u90e8\u7f72\u7ed3\u679c', blank=True)),
                ('create_dtm', models.DateTimeField(auto_now_add=True, verbose_name='\u6dfb\u52a0\u65f6\u95f4')),
            ],
        ),
        migrations.CreateModel(
            name='ClusterIp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.GenericIPAddressField(unique=True, verbose_name='IP\u5730\u5740')),
                ('device', models.CharField(help_text='\u53c2\u8003: eth0 [\u6700\u540e\u4e00\u4f4d\u662f\u6570\u5b57\u96f6]', max_length=100, verbose_name='\u8bbe\u5907\u540d')),
                ('netmask', models.CharField(help_text='\u53c2\u8003: 255.255.255.0.', max_length=255, verbose_name='\u5b50\u7f51\u63a9\u7801')),
                ('helo', models.CharField(max_length=200, verbose_name='helo')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528', choices=[(True, '\u662f'), (False, '\u5426')])),
                ('cluster', models.ForeignKey(related_name='cluster', to='core.Cluster')),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=50, verbose_name='\u5ba2\u6237\u5e10\u53f7')),
                ('password', models.CharField(max_length=128, verbose_name='\u5bc6\u7801')),
                ('company', models.CharField(max_length=50, verbose_name='\u516c\u53f8\u540d\u79f0')),
                ('service_start', models.DateField(verbose_name='\u670d\u52a1\u5f00\u59cb\u65f6\u95f4')),
                ('service_end', models.DateField(verbose_name='\u670d\u52a1\u5230\u671f\u65f6\u95f4')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528', choices=[(True, '\u662f'), (False, '\u5426')])),
            ],
        ),
        migrations.CreateModel(
            name='CustomerDomain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=100, verbose_name='\u5ba2\u6237\u4fe1\u4efb\u53d1\u9001\u57df\u540d')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('customer', models.ForeignKey(related_name='domain', to='core.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerIp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.GenericIPAddressField(verbose_name='\u5ba2\u6237\u56fa\u5b9aip')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('customer', models.ForeignKey(related_name='ip', to='core.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerMailbox',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mailbox', models.CharField(max_length=100, verbose_name='\u90ae\u7bb1\u5e10\u53f7')),
                ('password', models.CharField(max_length=100, verbose_name='\u90ae\u7bb1\u5bc6\u7801')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('customer', models.ForeignKey(related_name='mailbox', to='core.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='IpPool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='\u53d1\u9001\u6c60\u540d\u79f0,\u5982\u666e\u901a\u6c601, \u5907\u4efd\u6c60', max_length=20, verbose_name='\u540d\u79f0')),
                ('type', models.CharField(max_length=10, verbose_name='\u53d1\u9001\u6c60\u7c7b\u578b', choices=[(b'auto', '\u81ea\u52a8\u6c60'), (b'backup', '\u5907\u4efd\u6c60')])),
                ('desp', models.TextField(null=True, verbose_name='\u63cf\u8ff0', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='ip_pool',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u5206\u914dIP\u53d1\u9001\u6c60', blank=True, to='core.IpPool', null=True),
        ),
        migrations.AddField(
            model_name='clusterip',
            name='ip_pool',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u5206\u914dIP\u53d1\u9001\u6c60', blank=True, to='core.IpPool', null=True),
        ),
    ]
