# Generated by Django 3.1.2 on 2020-10-10 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20201008_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='token',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
