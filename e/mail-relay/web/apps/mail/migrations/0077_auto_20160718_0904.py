# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0076_subjectkeywordwhitelist_is_regex'),
    ]

    operations = [
        migrations.AddField(
            model_name='customkeywordblacklist',
            name='c_direct_reject',
            field=models.BooleanField(default=False, verbose_name='\u7f51\u5173,\u662f\u5426\u4e0d\u7528\u5ba1\u6838\uff0c\u76f4\u63a5\u62d2\u7edd'),
        ),
        migrations.AddField(
            model_name='customkeywordblacklist',
            name='collect',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4ee3\u6536'),
        ),
        migrations.AddField(
            model_name='customkeywordblacklist',
            name='direct_reject',
            field=models.BooleanField(default=False, verbose_name='\u4e2d\u7ee7,\u662f\u5426\u4e0d\u7528\u5ba1\u6838\uff0c\u76f4\u63a5\u62d2\u7edd'),
        ),
        migrations.AddField(
            model_name='customkeywordblacklist',
            name='relay',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4e2d\u7ee7'),
        ),
        migrations.AddField(
            model_name='noticesettings',
            name='collect_content',
            field=models.TextField(help_text='\u7f51\u5173\u7528\u6237\u6536\u4ef6\u4eba\u6570\u9650\u5236\uff0c\u8d85\u8fc7\u5c31\u8b66\u544a\u7ba1\u7406\u5458\u548c\u9500\u552e,\u652f\u6301\u53d8\u91cf: {company}(ID\uff1a{company_id})\u8868\u793a\u516c\u53f8\u4ee5\u53ca\u516c\u53f8ID, {setting}\u8868\u793a\u8bbe\u7f6e\u7684\u9650\u5236\u503c, {count}\u8868\u793a\u7f51\u5173\u6536\u4ef6\u4eba\u6570, {account}\u8868\u793a\u7f51\u5173\u6536\u4ef6\u90ae\u7bb1', null=True, verbose_name='\u7f51\u5173\u7528\u6237\u9650\u5236\u901a\u77e5', blank=True),
        ),
        migrations.AddField(
            model_name='noticesettings',
            name='relay_content',
            field=models.TextField(help_text='\u4e2d\u7ee7\u7528\u6237\u53d1\u4ef6\u4eba\u6570\u9650\u5236\uff0c\u8d85\u8fc7\u5c31\u8b66\u544a\u7ba1\u7406\u5458\u548c\u9500\u552e,\u652f\u6301\u53d8\u91cf: {company}(ID\uff1a{company_id})\u8868\u793a\u516c\u53f8\u4ee5\u53ca\u516c\u53f8ID, {setting}\u8868\u793a\u8bbe\u7f6e\u7684\u9650\u5236\u503c, {count}\u8868\u793a\u4e2d\u7ee7\u53d1\u4ef6\u4eba\u6570, {account}\u8868\u793a\u4e2d\u7ee7\u53d1\u4ef6\u90ae\u7bb1', null=True, verbose_name='\u4e2d\u7ee7\u7528\u6237\u9650\u5236\u901a\u77e5', blank=True),
        ),
        migrations.AddField(
            model_name='subjectkeywordwhitelist',
            name='c_direct_reject',
            field=models.BooleanField(default=False, verbose_name='\u7f51\u5173,\u662f\u5426\u4e0d\u7528\u5ba1\u6838\uff0c\u76f4\u63a5\u62d2\u7edd'),
        ),
        migrations.AddField(
            model_name='subjectkeywordwhitelist',
            name='collect',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4ee3\u6536'),
        ),
        migrations.AddField(
            model_name='subjectkeywordwhitelist',
            name='direct_reject',
            field=models.BooleanField(default=False, verbose_name='\u4e2d\u7ee7,\u662f\u5426\u4e0d\u7528\u5ba1\u6838\uff0c\u76f4\u63a5\u62d2\u7edd'),
        ),
        migrations.AddField(
            model_name='subjectkeywordwhitelist',
            name='relay',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u7528\u4e8e\u4e2d\u7ee7'),
        ),
    ]
