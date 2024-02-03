# Generated by Django 4.2.3 on 2023-08-06 23:16

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('ip_address', models.CharField(max_length=200)),
                ('username', models.CharField(max_length=200)),
                ('password', models.CharField(max_length=200)),
                ('eth_card', models.CharField(max_length=200, null=True)),
                ('ipv6', models.CharField(max_length=200, null=True)),
                ('ipv4', models.CharField(max_length=200, null=True)),
                ('location', models.CharField(max_length=200, null=True)),
                ('used_port', models.TextField(null=True, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
            ],
        ),
        migrations.CreateModel(
            name='ServerLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('command', models.TextField()),
                ('output', models.TextField()),
                ('error', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sunucu.server')),
            ],
        ),
    ]