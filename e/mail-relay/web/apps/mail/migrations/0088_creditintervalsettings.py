# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0087_checksettings_credit'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditIntervalSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credit_b', models.IntegerField(default=0, help_text='\u5f53\u53d1\u4ef6\u4eba\u4fe1\u8a89\u5ea6\u5927\u4e8e\u7b49\u4e8e\u533a\u95f4\u8d77\u3001\u5c0f\u4e8e\u533a\u95f4\u6b62\u65f6\uff0c\u6bcf\u5929\u53ef\u4ee5\u53d1\u9001\u76f8\u540c\u4e3b\u9898XX\u5c01\u90ae\u4ef6\uff0cXX\u5206\u949f\u5185\u5141\u8bb8\u53d1\u9001XX\u5c01\u90ae\u4ef6', verbose_name='\u4fe1\u8a89\u5ea6\u533a\u95f4\u8d77')),
                ('credit_e', models.IntegerField(default=0, help_text='\u9ed8\u8ba4\u503c\uff1a0\uff0c0\u8868\u793a\u65e0\u7a77\u5927', verbose_name='\u4fe1\u8a89\u5ea6\u533a\u95f4\u6b62')),
                ('bulk_max', models.IntegerField(default=10, help_text='24\u5c0f\u65f6\u5185,\u76f8\u540c\u4e3b\u9898\u7684\u90ae\u4ef6\u8d85\u8fc7\u8be5\u503c,\u5219\u88ab\u8ba4\u4e3a\u662f\u7fa4\u53d1\u90ae\u4ef6', verbose_name='\u7fa4\u53d1\u90ae\u4ef6\u9600\u503c')),
                ('bulk_sender_time', models.IntegerField(default=10, help_text='\u5355\u4f4d\uff1a\u5206\u949f\uff0c\u7fa4\u53d1\u76d1\u6d4b\u5355\u4e2a\u53d1\u4ef6\u4eba\u7684\u65f6\u95f4', verbose_name='\u7fa4\u53d1\u5355\u4e2a\u53d1\u4ef6\u4eba\u76d1\u6d4b\u65f6\u95f4')),
                ('bulk_sender_max', models.IntegerField(default=10, help_text='\u5355\u4e2a\u53d1\u4ef6\u4eba\u5728\u76d1\u6d4b\u65f6\u95f4\u5185\u5141\u8bb8\u53d1\u7684\u90ae\u4ef6\u5c01\u6570\uff0c\u8d85\u8fc7\u7684\u63a5\u6536\u5e76\u4e22\u5f03\uff0c\u5c06\u90ae\u4ef6\u6570\u8ba1\u5165\u7fa4\u53d1', verbose_name='\u7fa4\u53d1\u5355\u4e2a\u53d1\u4ef6\u4eba\u53d1\u9001\u9600\u503c')),
            ],
        ),
    ]
