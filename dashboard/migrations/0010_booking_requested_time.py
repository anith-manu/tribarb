# Generated by Django 3.1.2 on 2020-10-11 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_auto_20201011_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='requested_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
