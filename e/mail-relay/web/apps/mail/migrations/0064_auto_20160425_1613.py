# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0063_senderblacklist_parent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attachmentblacklist',
            options={'ordering': ('order',)},
        ),
        migrations.RemoveField(
            model_name='attachmentblacklist',
            name='disabled',
        ),
        migrations.AddField(
            model_name='attachmentblacklist',
            name='c_direct_reject',
            field=models.BooleanField(default=False, verbose_name='\u7f51\u5173,\u662f\u5426\u4e0d\u7528\u5ba1\u6838\uff0c\u76f4\u63a5\u62d2\u7edd'),
        ),
        migrations.AddField(
            model_name='attachmentblacklist',
            name='direct_reject',
            field=models.BooleanField(default=False, verbose_name='\u4e2d\u7ee7,\u662f\u5426\u4e0d\u7528\u5ba1\u6838\uff0c\u76f4\u63a5\u62d2\u7edd'),
        ),
        migrations.AddField(
            model_name='attachmentblacklist',
            name='order',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attachmentblacklist',
            name='parent',
            field=models.ForeignKey(related_name='children', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='mail.AttachmentBlacklist', null=True),
        ),
    ]
