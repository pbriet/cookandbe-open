# Generated by Django 2.0.8 on 2018-09-12 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_mgr', '0016_auto_20180205_1812'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='perceived_healthy',
            field=models.BooleanField(default=True),
        ),
    ]
