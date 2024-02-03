# Generated by Django 4.2.3 on 2023-08-09 21:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='credit_card_number',
            new_name='hash',
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='cvv',
            new_name='post_hash',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='month',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='name_surname',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='user',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='year',
        ),
    ]