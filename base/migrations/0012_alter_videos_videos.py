# Generated by Django 4.2.1 on 2023-06-26 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_videos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videos',
            name='videos',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]