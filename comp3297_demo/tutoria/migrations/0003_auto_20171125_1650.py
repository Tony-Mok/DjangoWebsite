# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-11-25 16:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutoria', '0002_auto_20171125_1354'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='booking',
        ),
        migrations.AddField(
            model_name='transaction',
            name='otherParty',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]