# Generated by Django 4.2.3 on 2024-01-06 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sunucu', '0003_server_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='image',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
