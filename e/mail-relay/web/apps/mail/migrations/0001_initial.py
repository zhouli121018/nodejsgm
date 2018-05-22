# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BounceSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('server', models.CharField(max_length=50, verbose_name='SMTP\u670d\u52a1\u5668')),
                ('port', models.IntegerField(default=25, verbose_name='\u7aef\u53e3')),
                ('is_ssl', models.BooleanField(default=False, verbose_name='SSL\u52a0\u5bc6')),
                ('mailbox', models.CharField(max_length=50, verbose_name='\u90ae\u7bb1\u5e10\u53f7')),
                ('password', models.CharField(max_length=50, verbose_name='\u90ae\u7bb1\u5bc6\u7801')),
                ('template_cn', models.TextField(help_text='\u652f\u6301\u53d8\u91cf: {reason}\u8868\u793a\u9000\u4fe1\u539f\u56e0, {origin}\u8868\u793a\u4e0d\u542b\u9644\u4ef6\u7684\u539f\u59cb\u90ae\u4ef6', verbose_name='\u4e2d\u6587\u6a21\u677f')),
                ('template_en', models.TextField(help_text='\u652f\u6301\u53d8\u91cf: {reason}\u8868\u793a\u9000\u4fe1\u539f\u56e0, {origin}\u8868\u793a\u4e0d\u542b\u9644\u4ef6\u7684\u539f\u59cb\u90ae\u4ef6', verbose_name='\u82f1\u6587\u6a21\u677f')),
            ],
        ),
        migrations.CreateModel(
            name='CheckSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bulk_max', models.IntegerField(default=10, help_text='24\u5c0f\u65f6\u5185,\u76f8\u540c\u4e3b\u9898\u7684\u90ae\u4ef6\u8d85\u8fc7\u8be5\u503c,\u5219\u88ab\u8ba4\u4e3a\u662f\u7fa4\u53d1\u90ae\u4ef6', verbose_name='\u7fa4\u53d1\u90ae\u4ef6\u9600\u503c')),
                ('bulk_expire', models.IntegerField(default=7, help_text='\u5355\u4f4d:\u5929\u6570, \u5982\u679c\u90ae\u4ef6\u88ab\u8ba4\u4e3a\u662f\u7fa4\u53d1\u90ae\u4ef6, \u5219\u76f8\u5e94\u5929\u6570\u91cc,\u76f8\u540c\u4e3b\u9898\u5c06\u88ab\u68c0\u6d4b', verbose_name='\u7fa4\u53d1\u90ae\u4ef6\u8fc7\u671f\u5929\u6570')),
                ('max_size', models.IntegerField(default=50, help_text='\u5355\u4f4d:M, \u80fd\u591f\u63a5\u6536\u7684\u90ae\u4ef6\u6700\u5927\u503c, \u9ed8\u8ba450M', verbose_name='\u90ae\u4ef6\u6700\u5927\u503c')),
                ('spam_score_max', models.FloatField(default=5.0, help_text='\u767d\u5929(07:00--19:00)\u5982\u679cspam\u68c0\u6d4b\u5206\u6570\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u88ab\u8ba4\u4e3a\u662f\u5783\u573e\u90ae\u4ef6, \u9ed8\u8ba4\u4e3a5.0', verbose_name='spam\u68c0\u6d4b\u5206\u6570\u9600\u503c(\u767d\u5929)')),
                ('night_spam_score_max', models.FloatField(default=4.0, help_text='\u665a\u4e0a(19:00--07:00)\u5982\u679cspam\u68c0\u6d4b\u5206\u6570\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u88ab\u8ba4\u4e3a\u662f\u5783\u573e\u90ae\u4ef6, \u9ed8\u8ba4\u4e3a5.0', verbose_name='spam\u68c0\u6d4b\u5206\u6570\u9600\u503c(\u665a\u4e0a)')),
                ('sender_max_size', models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u90ae\u4ef6\u5982\u679c\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u76f4\u63a5\u653e\u884c, \u4e0d\u8fdb\u884c\u68c0\u6d4b, \u9ed8\u8ba40KB, \u8868\u793a\u5168\u90e8\u68c0\u6d4b', verbose_name='\u53d1\u4ef6\u4eba\u68c0\u6d4b\u9600\u503c')),
                ('subject_max_size', models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u90ae\u4ef6\u5982\u679c\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u76f4\u63a5\u653e\u884c, \u4e0d\u8fdb\u884c\u68c0\u6d4b, \u9ed8\u8ba40KB, \u8868\u793a\u5168\u90e8\u68c0\u6d4b', verbose_name='\u4e3b\u9898\u68c0\u6d4b\u9600\u503c')),
                ('content_max_size', models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u90ae\u4ef6\u5982\u679c\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u76f4\u63a5\u653e\u884c, \u4e0d\u8fdb\u884c\u68c0\u6d4b, \u9ed8\u8ba40KB, \u8868\u793a\u5168\u90e8\u68c0\u6d4b', verbose_name='\u5185\u5bb9\u68c0\u6d4b\u9600\u503c')),
                ('spam_max_size', models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u90ae\u4ef6\u5982\u679c\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u76f4\u63a5\u653e\u884c, \u4e0d\u8fdb\u884c\u68c0\u6d4b, \u9ed8\u8ba40KB, \u8868\u793a\u5168\u90e8\u68c0\u6d4b', verbose_name='Spamassassin\u68c0\u6d4b\u9600\u503c')),
                ('dspam_max_size', models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u90ae\u4ef6\u5982\u679c\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u76f4\u63a5\u653e\u884c, \u4e0d\u8fdb\u884c\u68c0\u6d4b, \u9ed8\u8ba40KB, \u8868\u793a\u5168\u90e8\u68c0\u6d4b', verbose_name='Dspam\u68c0\u6d4b\u9600\u503c')),
                ('custom_max_size', models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u90ae\u4ef6\u5982\u679c\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u76f4\u63a5\u653e\u884c, \u4e0d\u8fdb\u884c\u68c0\u6d4b, \u9ed8\u8ba40KB, \u8868\u793a\u5168\u90e8\u68c0\u6d4b', verbose_name='\u81ea\u52a8\u56de\u590d\u68c0\u6d4b\u9600\u503c')),
                ('attachment_min_size', models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u90ae\u4ef6\u9644\u4ef6\u662frar\u6216zip\u7c7b\u578b\uff0c\u4e14\u5927\u5c0f\u5c0f\u4e8e\u8be5\u9600\u503c, \u5219\u8ba4\u4e3a\u662f\u9ad8\u5371\u90ae\u4ef6, \u9ed8\u8ba40KB, \u8868\u793a\u4e0d\u68c0\u6d4b', verbose_name='\u5c0f\u5371\u9644\u4ef6\u9600\u503c')),
            ],
        ),
        migrations.CreateModel(
            name='CustomKeywordBlacklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u90ae\u4ef6\u5185\u5bb9\u6216\u4e3b\u9898\u5982\u679c\u542b\u6709\u9ed1\u540d\u5355\u5173\u952e\u8bcd\uff0c\u5219\u5c06\u8be5\u90ae\u4ef6\u6302\u8d77\u5e76\u4ea4\u7ed9\u7ba1\u7406\u5458\u5ba1\u6838,\u652f\u6301\u901a\u914d\u7b26?\uff0c\u4f8b\u5982\u201c\u53d1.{1}\u7968\u201d\u6216\u201c\u53d1.{2}\u7968\u201d\uff0c\u8fd9\u6837\uff0c\u5219\u201c\u53d1a\u7968\u201d \u6216 \u201c\u53d1aa\u7968\u201d', max_length=50, verbose_name='\u81ea\u52a8\u56de\u590d\u5173\u952e\u5b57')),
                ('type', models.CharField(default=b'subject', max_length=10, verbose_name='\u68c0\u6d4b\u7c7b\u578b', choices=[(b'subject', '\u4e3b\u9898'), (b'content', '\u5185\u5bb9')])),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('hits', models.IntegerField(default=0, verbose_name='\u547d\u4e2d\u6b21\u6570')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
        migrations.CreateModel(
            name='DeliverLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.CharField(max_length=20, verbose_name='\u65e5\u671f')),
                ('mail_id', models.IntegerField()),
                ('deliver_time', models.DateTimeField(null=True, verbose_name='\u53d1\u9001\u65f6\u95f4', blank=True)),
                ('deliver_ip', models.GenericIPAddressField(null=True, verbose_name='\u53d1\u9001IP', blank=True)),
                ('receive_ip', models.GenericIPAddressField(null=True, verbose_name='\u63a5\u6536IP', blank=True)),
                ('return_code', models.SmallIntegerField(null=True, blank=True)),
                ('return_message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='DomainBlacklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(help_text='\u53d1\u4ef6\u4eba\u5982\u679c\u5305\u542b\u67d0\u4e9b\u57df\u540d\uff0c\u6bd4\u5982qq.com 163.com\uff0c\u8fd9\u6837\u7684\u90ae\u4ef6\u63a5\u6536\u540e\u5220\u9664\uff0c\u652f\u6301\u901a\u914d\u7b26\u5f55\u5165\u9ed1\u540d\u5355\u6570\u636e\uff0c\u4f8b\u5982.*\\.yahoo\\..* (\u8fd9\u4e2a\u4ee3\u8868*.yahoo.com   *.yahoo.com.cn   *.yahoo.jp\u7b49) ', max_length=50, verbose_name='\u57df\u540d\u5173\u952e\u5b57')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('hits', models.IntegerField(default=0, verbose_name='\u547d\u4e2d\u6b21\u6570')),
            ],
        ),
        migrations.CreateModel(
            name='InvalidMail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mail', models.CharField(help_text='\u65e0\u6548\u90ae\u4ef6\u5730\u5740', unique=True, max_length=100, verbose_name='\u90ae\u4ef6\u5730\u5740', db_index=True)),
                ('hits', models.IntegerField(default=0, verbose_name='\u547d\u4e2d\u6b21\u6570')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
        migrations.CreateModel(
            name='KeywordBlacklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u90ae\u4ef6\u5185\u5bb9\u5982\u679c\u542b\u6709\u9ed1\u540d\u5355\u5173\u952e\u8bcd\uff0c\u5219\u5c06\u8be5\u90ae\u4ef6\u6302\u8d77\u5e76\u4ea4\u7ed9\u7ba1\u7406\u5458\u5ba1\u6838,\u652f\u6301\u901a\u914d\u7b26?\uff0c\u4f8b\u5982\u201c\u53d1.{1}\u7968\u201d\u6216\u201c\u53d1.{2}\u7968\u201d\uff0c\u8fd9\u6837\uff0c\u5219\u201c\u53d1a\u7968\u201d \u6216 \u201c\u53d1aa\u7968\u201d', max_length=50, verbose_name='\u5185\u5bb9\u5173\u952e\u5b57')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('hits', models.IntegerField(default=0, verbose_name='\u547d\u4e2d\u6b21\u6570')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
        migrations.CreateModel(
            name='RecipientBlacklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u6536\u4ef6\u4eba\u5982\u679c\u542b\u6709\u9ed1\u540d\u5355\u5173\u952e\u8bcd\uff0c\u5219\u5c06\u8be5\u90ae\u4ef6\u5f53\u65e0\u6548\u6536\u4ef6\u5730\u5740\u5904\u7406, \u652f\u6301\u6b63\u5219\u8868\u8fbe\u5f0f', max_length=50, verbose_name='\u5173\u952e\u5b57')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('hits', models.IntegerField(default=0, verbose_name='\u547d\u4e2d\u6b21\u6570')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
        migrations.CreateModel(
            name='SenderBlacklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u6536\u4ef6\u4eba\u5982\u679c\u542b\u6709\u9ed1\u540d\u5355\u5173\u952e\u8bcd\uff0c\u5219\u5c06\u8be5\u90ae\u4ef6\u6302\u8d77,\u4ea4\u7ed9\u7ba1\u7406\u5458\u5ba1\u6838,\u652f\u6301\u6b63\u5219\u8868\u8fbe\u5f0f', max_length=50, verbose_name='\u5173\u952e\u5b57')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('hits', models.IntegerField(default=0, verbose_name='\u547d\u4e2d\u6b21\u6570')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('retry_mode', models.CharField(default=b'single_ip', max_length=20, verbose_name='\u91cd\u8bd5\u65b9\u5f0f', choices=[(b'single_ip', '\u5355IP\u8f6e\u8be2'), (b'multi_ip', '\u591aIP\u8f6e\u8be2')])),
            ],
        ),
        migrations.CreateModel(
            name='SpfError',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(help_text='spf\u9519\u8bef\u57df\u540d', max_length=200, verbose_name='\u57df\u540d\u5173\u952e\u5b57')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Customer', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u65e5\u671f')),
                ('type', models.CharField(max_length=20, verbose_name='\u7c7b\u578b', choices=[(b'all', '\u5168\u90e8'), (b'ip', 'IP'), (b'ip_pool', 'IP\u6c60'), (b'cluster', 'SMTP\u53d1\u9001\u673a'), (b'customer', '\u5ba2\u6237')])),
                ('count', models.IntegerField(default=0, verbose_name='\u603b\u6570')),
                ('success', models.IntegerField(default=0, verbose_name='\u6210\u529f\u6570')),
                ('fail', models.IntegerField(default=0, verbose_name='\u5931\u8d25\u6570')),
                ('error_type_1', models.IntegerField(default=0, verbose_name='\u8fde\u63a5\u9519\u8bef')),
                ('error_type_2', models.IntegerField(default=0, verbose_name='\u4e0d\u5b58\u5728\u9519\u8bef')),
                ('error_type_3', models.IntegerField(default=0, verbose_name='\u5176\u4ed6\u9519\u8bef')),
                ('error_type_4', models.IntegerField(default=0, verbose_name='\u8d85\u5927/\u6ee1\u7684\u90ae\u4ef6')),
                ('error_type_5', models.IntegerField(default=0, verbose_name='\u5783\u573e\u90ae\u4ef6')),
                ('error_type_6', models.IntegerField(default=0, verbose_name='\u4e0d\u91cd\u8bd5\u90ae\u4ef6')),
                ('error_type_7', models.IntegerField(default=0, verbose_name='spf\u90ae\u4ef6')),
                ('rate', models.FloatField(default=0, verbose_name='\u6210\u529f\u6bd4')),
                ('ip', models.CharField(max_length=20, null=True, verbose_name='IP', blank=True)),
                ('cluster', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Cluster', null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Customer', null=True)),
                ('ip_pool', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.IpPool', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubjectKeywordBlacklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u90ae\u4ef6\u4e3b\u9898\u5982\u679c\u542b\u6709\u9ed1\u540d\u5355\u5173\u952e\u8bcd\uff0c\u5219\u5c06\u8be5\u90ae\u4ef6\u6302\u8d77\u5e76\u4ea4\u7ed9\u7ba1\u7406\u5458\u5ba1\u6838,\u652f\u6301\u901a\u914d\u7b26?\uff0c\u4f8b\u5982\u201c\u53d1.{1}\u7968\u201d\u6216\u201c\u53d1.{2}\u7968\u201d\uff0c\u8fd9\u6837\uff0c\u5219\u201c\u53d1a\u7968\u201d \u6216 \u201c\u53d1aa\u7968\u201d', max_length=50, verbose_name='\u4e3b\u9898\u5173\u952e\u5b57')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('hits', models.IntegerField(default=0, verbose_name='\u547d\u4e2d\u6b21\u6570')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
        migrations.CreateModel(
            name='SubjectKeywordWhitelist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(help_text='\u90ae\u4ef6\u4e3b\u9898\u5982\u679c\u542b\u6709\u767d\u540d\u5355\u5173\u952e\u8bcd\uff0c\u5219\u5c06\u8be5\u90ae\u4ef6\u4e0d\u4f1a\u8fdb\u884c\u7fa4\u53d1\u90ae\u4ef6\u68c0\u6d4b,\u652f\u6301\u901a\u914d\u7b26?\uff0c\u4f8b\u5982\u201c\u53d1.{1}\u7968\u201d\u6216\u201c\u53d1.{2}\u7968\u201d\uff0c\u8fd9\u6837\uff0c\u5219\u201c\u53d1a\u7968\u201d \u6216 \u201c\u53d1aa\u7968\u201d', max_length=50, verbose_name='\u4e3b\u9898\u5173\u952e\u5b57')),
                ('disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('hits', models.IntegerField(default=0, verbose_name='\u547d\u4e2d\u6b21\u6570')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
        migrations.AlterIndexTogether(
            name='deliverlog',
            index_together=set([('date', 'mail_id')]),
        ),
    ]
