# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0062_auto_20170527_1100'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerLocalizedSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(max_length=50, null=True, verbose_name='\u8bbf\u95ee\u6743\u9650Token', blank=True)),
                ('ip', models.CharField(max_length=20, verbose_name='\u5ba2\u6237ip')),
                ('customer', models.ForeignKey(to='core.Customer', unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='customersetting',
            name='check_autoreply',
            field=models.BooleanField(default=True, help_text='\u9009\u4e2d\u5373\u4e3a\u5f00\u542f\uff0c\u5f00\u542f\u8868\u793a\u8fc7\u6ee4"\u81ea\u52a8\u56de\u590d"\u90ae\u4ef6,\u9ed8\u8ba4\u5f00\u542f', verbose_name='\u4e2d\u7ee7\u8fc7\u6ee4:\u81ea\u52a8\u56de\u590d'),
        ),
    ]
