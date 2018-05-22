# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0034_auto_20160127_1139'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckStatistics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u65e5\u671f')),
                ('active_spam_all', models.IntegerField(default=0, verbose_name='\u52a8\u6001SPAM\u5168\u90e8')),
                ('active_spam_pass', models.IntegerField(default=0, verbose_name='\u52a8\u6001SPAM\u901a\u8fc7')),
                ('high_risk_all', models.IntegerField(default=0, verbose_name='\u9ad8\u5371\u90ae\u4ef6\u5168\u90e8')),
                ('high_risk_pass', models.IntegerField(default=0, verbose_name='\u9ad8\u5371\u90ae\u4ef6\u901a\u8fc7')),
                ('keyword_blacklist_all', models.IntegerField(default=0, verbose_name='\u5185\u5bb9\u9ed1\u5168\u90e8')),
                ('keyword_blacklist_pass', models.IntegerField(default=0, verbose_name='\u5185\u5bb9\u9ed1\u901a\u8fc7')),
                ('sender_blacklist_all', models.IntegerField(default=0, verbose_name='\u53d1\u4ef6\u9ed1\u5168\u90e8')),
                ('sender_blacklist_pass', models.IntegerField(default=0, verbose_name='\u53d1\u4ef6\u9ed1\u901a\u8fc7')),
                ('subject_blacklist_all', models.IntegerField(default=0, verbose_name='\u4e3b\u9898\u9ed1\u5168\u90e8')),
                ('subject_blacklist_pass', models.IntegerField(default=0, verbose_name='\u4e3b\u9898\u9ed1\u901a\u8fc7')),
                ('cyber_spam_all', models.IntegerField(default=0, verbose_name='cyber\u5168\u90e8')),
                ('cyber_spam_pass', models.IntegerField(default=0, verbose_name='cyber\u901a\u8fc7')),
                ('spamassassin_all', models.IntegerField(default=0, verbose_name='spam\u5168\u90e8')),
                ('spamassassin_pass', models.IntegerField(default=0, verbose_name='spam\u901a\u8fc7')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
            ],
        ),
    ]
