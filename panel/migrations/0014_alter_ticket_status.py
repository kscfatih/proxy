# Generated by Django 4.2.3 on 2023-11-25 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0013_alter_ticket_report_processed_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending'), ('answered', 'Answered'), ('closed', 'Closed')], max_length=200, null=True),
        ),
    ]
