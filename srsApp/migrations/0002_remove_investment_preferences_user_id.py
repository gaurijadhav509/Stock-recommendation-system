# Generated by Django 5.1.3 on 2024-11-17 03:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("srsApp", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="investment_preferences",
            name="user_id",
        ),
    ]