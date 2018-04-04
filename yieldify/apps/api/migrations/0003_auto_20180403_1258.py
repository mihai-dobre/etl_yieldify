# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-03 12:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20180402_1127'),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='agent',
            name='browser_version',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='agent',
            name='device_brand',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='agent',
            name='device_type',
            field=models.CharField(blank=True, choices=[('mobile', 'mobile'), ('laptop', 'laptop'), ('tablet', 'tablet'), ('desktop', 'desktop'), ('bot', 'bot'), ('unknown', 'unknown')], max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='agent',
            name='op_sys_version',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='request',
            name='agent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Agent'),
        ),
        migrations.AddField(
            model_name='request',
            name='file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.InputFile'),
        ),
        migrations.AddField(
            model_name='request',
            name='ip',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.IP'),
        ),
        migrations.AddField(
            model_name='request',
            name='url',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Url'),
        ),
        migrations.AddField(
            model_name='request',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.CustomUser'),
        ),
    ]