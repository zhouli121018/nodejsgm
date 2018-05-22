# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collect', '0002_auto_20151029_1403'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('spam_score_max', models.FloatField(default=5.0, help_text='\u767d\u5929(07:00--19:00)\u5982\u679cspam\u68c0\u6d4b\u5206\u6570\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u88ab\u8ba4\u4e3a\u662f\u5783\u573e\u90ae\u4ef6, \u9ed8\u8ba4\u4e3a5.0', verbose_name='spam\u68c0\u6d4b\u5206\u6570\u9600\u503c(\u767d\u5929)')),
                ('night_spam_score_max', models.FloatField(default=4.0, help_text='\u665a\u4e0a(19:00--07:00)\u5982\u679cspam\u68c0\u6d4b\u5206\u6570\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u88ab\u8ba4\u4e3a\u662f\u5783\u573e\u90ae\u4ef6, \u9ed8\u8ba4\u4e3a5.0', verbose_name='spam\u68c0\u6d4b\u5206\u6570\u9600\u503c(\u665a\u4e0a)')),
                ('subject_max_size', models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u90ae\u4ef6\u5982\u679c\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u76f4\u63a5\u653e\u884c, \u4e0d\u8fdb\u884c\u68c0\u6d4b, \u9ed8\u8ba40KB, \u8868\u793a\u5168\u90e8\u68c0\u6d4b', verbose_name='\u4e3b\u9898\u68c0\u6d4b\u9600\u503c')),
                ('content_max_size', models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u90ae\u4ef6\u5982\u679c\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u76f4\u63a5\u653e\u884c, \u4e0d\u8fdb\u884c\u68c0\u6d4b, \u9ed8\u8ba40KB, \u8868\u793a\u5168\u90e8\u68c0\u6d4b', verbose_name='\u5185\u5bb9\u68c0\u6d4b\u9600\u503c')),
                ('spam_max_size', models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u90ae\u4ef6\u5982\u679c\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u76f4\u63a5\u653e\u884c, \u4e0d\u8fdb\u884c\u68c0\u6d4b, \u9ed8\u8ba40KB, \u8868\u793a\u5168\u90e8\u68c0\u6d4b', verbose_name='Spamassassin\u68c0\u6d4b\u9600\u503c')),
                ('dspam_max_size', models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u90ae\u4ef6\u5982\u679c\u8d85\u8fc7\u8be5\u9600\u503c, \u5219\u76f4\u63a5\u653e\u884c, \u4e0d\u8fdb\u884c\u68c0\u6d4b, \u9ed8\u8ba40KB, \u8868\u793a\u5168\u90e8\u68c0\u6d4b', verbose_name='Dspam\u68c0\u6d4b\u9600\u503c')),
                ('attachment_min_size', models.IntegerField(default=0, help_text='\u5355\u4f4d:KB, \u90ae\u4ef6\u9644\u4ef6\u662frar\u6216zip\u7c7b\u578b\uff0c\u4e14\u5927\u5c0f\u5c0f\u4e8e\u8be5\u9600\u503c, \u5219\u8ba4\u4e3a\u662f\u9ad8\u5371\u90ae\u4ef6, \u9ed8\u8ba40KB, \u8868\u793a\u4e0d\u68c0\u6d4b', verbose_name='\u5c0f\u5371\u9644\u4ef6\u9600\u503c')),
            ],
        ),
        migrations.CreateModel(
            name='DeliverLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.CharField(max_length=20, verbose_name='\u65e5\u671f')),
                ('mail_id', models.IntegerField()),
                ('deliver_ip', models.GenericIPAddressField(null=True, verbose_name='\u53d1\u9001IP', blank=True)),
                ('deliver_time', models.DateTimeField(null=True, verbose_name='\u53d1\u9001\u65f6\u95f4', blank=True)),
                ('mx_record', models.CharField(max_length=200, null=True, verbose_name='mx \u8bb0\u5f55', blank=True)),
                ('receive_ip', models.GenericIPAddressField(null=True, verbose_name='\u63a5\u6536IP', blank=True)),
                ('return_code', models.SmallIntegerField(null=True, blank=True)),
                ('return_message', models.TextField()),
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
            name='Settings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('back_days', models.IntegerField(default=30, help_text='\u5355\u4f4d\uff1a\u5929\u6570\uff0c\u8d85\u8fc7\u8be5\u5929\u6570\u7684\u539f\u59cb\u90ae\u4ef6\u5c06\u4f1a\u88ab\u81ea\u52a8\u6e05\u9664', verbose_name='\u90ae\u4ef6\u5907\u4efd\u65e5\u671f')),
                ('expired_days', models.IntegerField(default=15, help_text='\u5355\u4f4d\uff1a\u5929\u6570\uff0c\u5982\u679c\u5ba2\u6237\u670d\u52a1\u5230\u671f\uff0c\u53ef\u5ef6\u957f\u53d1\u9001\u76f8\u5e94\u5929\u6570', verbose_name='\u5ba2\u6237\u8fc7\u671f\u5ef6\u957f\u5929\u6570')),
            ],
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u65e5\u671f')),
                ('type', models.CharField(max_length=20, verbose_name='\u7c7b\u578b', choices=[(b'all', '\u5168\u90e8'), (b'customer', '\u5ba2\u6237')])),
                ('count', models.IntegerField(default=0, verbose_name='\u603b\u6570')),
                ('success', models.IntegerField(default=0, verbose_name='\u6210\u529f\u6570')),
                ('fail', models.IntegerField(default=0, verbose_name='\u5931\u8d25\u6570')),
                ('rate', models.FloatField(default=0, verbose_name='\u6210\u529f\u6bd4')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='collect.ColCustomer', null=True)),
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
        migrations.AlterIndexTogether(
            name='deliverlog',
            index_together=set([('date', 'mail_id')]),
        ),
    ]
