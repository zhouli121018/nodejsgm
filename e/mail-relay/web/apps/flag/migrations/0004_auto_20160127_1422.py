# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('flag', '0003_auto_20151109_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='bigquotaflag',
            name='creater',
            field=models.ForeignKey(related_name='creater17', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='bigquotaflag',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='bigquotaflag',
            name='operater',
            field=models.ForeignKey(related_name='operater17', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='highriskflag',
            name='creater',
            field=models.ForeignKey(related_name='creater21', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='highriskflag',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='highriskflag',
            name='operater',
            field=models.ForeignKey(related_name='operater21', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='notexistflag',
            name='creater',
            field=models.ForeignKey(related_name='creater16', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='notexistflag',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='notexistflag',
            name='operater',
            field=models.ForeignKey(related_name='operater16', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='notretryflag',
            name='creater',
            field=models.ForeignKey(related_name='creater19', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='notretryflag',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='notretryflag',
            name='operater',
            field=models.ForeignKey(related_name='operater19', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='spamflag',
            name='creater',
            field=models.ForeignKey(related_name='creater18', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='spamflag',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='spamflag',
            name='operater',
            field=models.ForeignKey(related_name='operater18', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='spfflag',
            name='creater',
            field=models.ForeignKey(related_name='creater20', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='spfflag',
            name='operate_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u64cd\u4f5c\u65e5\u671f', null=True),
        ),
        migrations.AddField(
            model_name='spfflag',
            name='operater',
            field=models.ForeignKey(related_name='operater20', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
