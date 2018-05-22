# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0064_customersetting_c_bounce'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerlocalizedsetting',
            name='port',
            field=models.IntegerField(default=10000, verbose_name='\u7aef\u53e3'),
        ),
        migrations.AlterField(
            model_name='customersetting',
            name='c_bounce',
            field=models.BooleanField(default=False, help_text='\u9009\u4e2d\u5373\u4e3a\u5f00\u542f,\u5f00\u542f\u8868\u793a\u7f51\u5173\u90ae\u4ef6\u51fa\u7ad9\u5931\u8d25(\u90ae\u4ef6\u4e0d\u5b58\u5728,\u8d85\u5927/\u6ee1,\u4e0d\u91cd\u8bd5),\u7cfb\u7edf\u4f1a\u81ea\u52a8\u9000\u4fe1', verbose_name='\u7f51\u5173:\u5f00\u542f\u9000\u4fe1'),
        ),
    ]
