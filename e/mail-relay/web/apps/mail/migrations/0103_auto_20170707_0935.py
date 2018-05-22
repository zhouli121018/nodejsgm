# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0102_noticesettings_service_limit_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noticesettings',
            name='service_limit_content',
            field=models.TextField(help_text='\u4e2d\u7ee7&\u7f51\u5173\u670d\u52a1\u5feb\u5230\u671f\u901a\u77e5\u5ba2\u6237, {customer}\u5ba2\u6237\u540d\u79f0, {type_info}\u670d\u52a1\u7c7b\u578b(\u7f51\u5173/\u4e2d\u7ee7) {days}\u670d\u52a1\u5373\u5c06\u5230\u671f\u5929\u6570, {expire_date}\u5230\u671f\u65e5\u671f', null=True, verbose_name='\u5ba2\u6237\u670d\u52a1\u5230\u671f\u901a\u77e5', blank=True),
        ),
    ]
