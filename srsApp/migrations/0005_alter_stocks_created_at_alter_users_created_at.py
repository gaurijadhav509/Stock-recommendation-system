# Generated by Django 5.1.2 on 2024-11-12 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('srsApp', '0004_alter_stocks_created_at_alter_users_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stocks',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='users',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]