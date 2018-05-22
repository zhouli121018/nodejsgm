# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0081_auto_20180320_1549'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customersummary',
            old_name='c_fail',
            new_name='c_fail_finished',
        ),
        migrations.RenameField(
            model_name='customersummary',
            old_name='c_fail_flow',
            new_name='c_fail_finished_flow',
        ),
        migrations.RenameField(
            model_name='customersummary',
            old_name='c_success',
            new_name='c_finished',
        ),
        migrations.RenameField(
            model_name='customersummary',
            old_name='c_success_flow',
            new_name='c_finished_flow',
        ),
        migrations.RenameField(
            model_name='customersummary',
            old_name='fail',
            new_name='fail_finished',
        ),
        migrations.RenameField(
            model_name='customersummary',
            old_name='fail_flow',
            new_name='fail_finished_flow',
        ),
        migrations.RenameField(
            model_name='customersummary',
            old_name='success',
            new_name='finished',
        ),
        migrations.RenameField(
            model_name='customersummary',
            old_name='success_flow',
            new_name='finished_flow',
        ),
    ]
