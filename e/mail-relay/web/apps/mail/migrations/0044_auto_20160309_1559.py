# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mail', '0043_auto_20160308_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='noticesettings',
            name='ip_content',
            field=models.TextField(help_text='\u5f53\u53d1\u9001\u673a\u8fde\u7eed10\u5206\u949f\u63a5\u6536\u90ae\u4ef6\u90fd\u5931\u8d25\u65f6\uff0c\u5219\u901a\u77e5\u76f8\u5e94\u7ba1\u7406\u5458\u8be5\u53d1\u9001\u673aIP\u4e0d\u901a,\u652f\u6301\u53d8\u91cf: {ip}\u8868\u793a\u53d1\u9001\u673aIP', null=True, verbose_name='IP\u4e0d\u901a\u901a\u77e5', blank=True),
        ),
        migrations.AddField(
            model_name='noticesettings',
            name='ip_interval',
            field=models.IntegerField(default=60, help_text='\u5355\u4f4d\uff1a\u5206\u949f\uff0cIP\u4e0d\u901a\u901a\u77e5\u53d1\u9001\u95f4\u9694\u65f6\u95f4', verbose_name='IP\u4e0d\u901a\u901a\u77e5\u95f4\u9694'),
        ),
        migrations.AddField(
            model_name='noticesettings',
            name='manager',
            field=models.ForeignKey(related_name='manager', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, help_text='\u9700\u901a\u77e5\u7684\u9ed8\u8ba4\u7ba1\u7406\u5458', null=True, verbose_name='\u9ed8\u8ba4\u7ba1\u7406\u5458'),
        ),
        migrations.AlterField(
            model_name='noticesettings',
            name='reviewer',
            field=models.ForeignKey(related_name='reviewer', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, help_text='\u9700\u901a\u77e5\u7684\u9ed8\u8ba4\u5ba1\u6838\u4eba\u5458', null=True, verbose_name='\u9ed8\u8ba4\u5ba1\u6838\u4eba\u5458'),
        ),
    ]
