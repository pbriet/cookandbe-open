# Generated by Django 4.2.7 on 2024-01-11 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diet_mgr', '0015_diet_rank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diet',
            name='url_key',
            field=models.CharField(db_index=True, max_length=500),
        ),
    ]
