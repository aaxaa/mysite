# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-07 10:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='answer_text',
            field=models.TextField(blank=True, null=True, verbose_name='\u7b54\u590d\u5185\u5bb9'),
        ),
    ]
