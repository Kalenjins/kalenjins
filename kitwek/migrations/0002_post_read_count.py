# Generated by Django 5.1.3 on 2025-02-01 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitwek', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='read_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
