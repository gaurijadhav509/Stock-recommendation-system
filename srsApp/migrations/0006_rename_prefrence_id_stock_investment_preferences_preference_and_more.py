# Generated by Django 5.1.2 on 2024-11-15 21:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('srsApp', '0005_rename_stock_id_user_bookmarked_stocks_stock_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stock_investment_preferences',
            old_name='prefrence_id',
            new_name='preference',
        ),
        migrations.RenameField(
            model_name='stock_investment_preferences',
            old_name='stock_id',
            new_name='stock',
        ),
        migrations.RenameField(
            model_name='user_investment_preferences',
            old_name='prefrence_id',
            new_name='preference',
        ),
        migrations.RenameField(
            model_name='user_investment_preferences',
            old_name='user_id',
            new_name='user',
        ),
        migrations.AlterUniqueTogether(
            name='stock_investment_preferences',
            unique_together={('stock', 'preference')},
        ),
        migrations.AlterUniqueTogether(
            name='user_investment_preferences',
            unique_together={('user', 'preference')},
        ),
    ]