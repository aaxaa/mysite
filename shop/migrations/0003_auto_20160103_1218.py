# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-03 04:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_auto_20160103_1203'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shopcart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_price', models.FloatField(verbose_name='\u603b\u4ef7')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Customer', verbose_name='\u5ba2\u6237')),
            ],
        ),
        migrations.CreateModel(
            name='ShopcartProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateField(verbose_name='\u6dfb\u52a0\u65f6\u95f4')),
                ('count', models.SmallIntegerField(verbose_name='\u6570\u91cf')),
                ('price', models.FloatField(verbose_name='\u4ef7\u683c')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Product')),
                ('shopcart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Shopcart')),
            ],
        ),
        migrations.RemoveField(
            model_name='order',
            name='booking_at',
        ),
        migrations.RemoveField(
            model_name='order',
            name='type',
        ),
        migrations.RemoveField(
            model_name='orderproduct',
            name='total',
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='price',
            field=models.FloatField(default=0.00, verbose_name='\u4ef7\u683c'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.SmallIntegerField(choices=[(0, '\u5df2\u521b\u5efa'), (1, '\u5df2\u4e0b\u5355'), (2, '\u672a\u652f\u4ed8'), (3, '\u5df2\u4ed8\u6b3e'), (4, '\u5f85\u5ba1\u6838'), (5, '\u5df2\u5ba1\u6838'), (6, '\u5df2\u53d1\u8d27'), (7, '\u5df2\u6d88\u8d39'), (8, '\u5df2\u5b8c\u6210')], default=0, verbose_name='\u72b6\u6001'),
        ),
        migrations.AddField(
            model_name='shopcart',
            name='products',
            field=models.ManyToManyField(through='shop.ShopcartProduct', to='shop.Product', verbose_name='\u5546\u54c1\u4fe1\u606f'),
        ),
    ]
