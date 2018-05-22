# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0097_spamrptsettings_m_html_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulkcustomer',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to='core.Customer', null=True),
        ),
        migrations.AlterField(
            model_name='customersenderblacklist',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to='core.Customer', null=True),
        ),
        migrations.AlterField(
            model_name='reviewstatistics',
            name='reviewer',
            field=models.ForeignKey(related_name='review_statistics', on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='senderblockedrecord',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to='core.Customer', null=True),
        ),
        migrations.AlterField(
            model_name='senderwhitelist',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to='core.Customer', null=True),
        ),
        migrations.AlterField(
            model_name='spferror',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to='core.Customer', null=True),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='customer',
            field=models.ForeignKey(related_name='relay_statistics', on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to='core.Customer', null=True),
        ),
        migrations.AlterField(
            model_name='tempsenderblacklist',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to='core.Customer', null=True),
        ),
    ]
