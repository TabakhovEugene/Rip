# Generated by Django 4.2.4 on 2024-10-12 09:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0007_alter_animal_created_at_alter_animal_moderator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animal',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 12, 12, 59, 44, 497391)),
        ),
    ]
