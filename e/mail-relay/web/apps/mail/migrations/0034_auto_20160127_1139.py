# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mail', '0033_auto_20160127_0958'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachmentblacklist',
            name='creater',
            field=models.ForeignKey(related_name='creater10', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='attachmentblacklist',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='attachmentblacklist',
            name='operater',
            field=models.ForeignKey(related_name='operater10', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='customkeywordblacklist',
            name='creater',
            field=models.ForeignKey(related_name='creater8', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='customkeywordblacklist',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='customkeywordblacklist',
            name='operater',
            field=models.ForeignKey(related_name='operater8', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='invalidmail',
            name='creater',
            field=models.ForeignKey(related_name='creater6', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='invalidmail',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='invalidmail',
            name='operater',
            field=models.ForeignKey(related_name='operater6', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='invalidsenderwhitelist',
            name='creater',
            field=models.ForeignKey(related_name='creater12', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='invalidsenderwhitelist',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='invalidsenderwhitelist',
            name='operater',
            field=models.ForeignKey(related_name='operater12', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='keywordblacklist',
            name='creater',
            field=models.ForeignKey(related_name='creater3', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='keywordblacklist',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='keywordblacklist',
            name='operater',
            field=models.ForeignKey(related_name='operater3', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='recipientblacklist',
            name='creater',
            field=models.ForeignKey(related_name='creater7', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='recipientblacklist',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='recipientblacklist',
            name='operater',
            field=models.ForeignKey(related_name='operater7', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='recipientwhitelist',
            name='creater',
            field=models.ForeignKey(related_name='creater15', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='recipientwhitelist',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='recipientwhitelist',
            name='operater',
            field=models.ForeignKey(related_name='operater15', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='senderblacklist',
            name='creater',
            field=models.ForeignKey(related_name='creater5', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='senderblacklist',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='senderblacklist',
            name='operater',
            field=models.ForeignKey(related_name='operater5', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='senderwhitelist',
            name='creater',
            field=models.ForeignKey(related_name='creater11', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='senderwhitelist',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='senderwhitelist',
            name='operater',
            field=models.ForeignKey(related_name='operater11', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='spfchecklist',
            name='creater',
            field=models.ForeignKey(related_name='creater13', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='spfchecklist',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='spfchecklist',
            name='operater',
            field=models.ForeignKey(related_name='operater13', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='subjectkeywordblacklist',
            name='creater',
            field=models.ForeignKey(related_name='creater2', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='subjectkeywordblacklist',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='subjectkeywordblacklist',
            name='operater',
            field=models.ForeignKey(related_name='operater2', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='subjectkeywordwhitelist',
            name='creater',
            field=models.ForeignKey(related_name='creater4', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='subjectkeywordwhitelist',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='subjectkeywordwhitelist',
            name='operater',
            field=models.ForeignKey(related_name='operater4', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='tempsenderblacklist',
            name='creater',
            field=models.ForeignKey(related_name='creater14', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='tempsenderblacklist',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='validmailsuffix',
            name='creater',
            field=models.ForeignKey(related_name='creater9', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='validmailsuffix',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='validmailsuffix',
            name='operater',
            field=models.ForeignKey(related_name='operater9', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='domainblacklist',
            name='creater',
            field=models.ForeignKey(related_name='creater1', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='domainblacklist',
            name='operater',
            field=models.ForeignKey(related_name='operater1', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='tempsenderblacklist',
            name='operater',
            field=models.ForeignKey(related_name='operater14', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
