# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-09-18 03:20
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=200)),
                ('html', models.TextField(verbose_name='HTML')),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('template_data', jsonfield.fields.JSONField(default=dict)),
                ('meta_data', jsonfield.fields.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('image', sorl.thumbnail.fields.ImageField(upload_to='uploads')),
            ],
        ),
    ]
