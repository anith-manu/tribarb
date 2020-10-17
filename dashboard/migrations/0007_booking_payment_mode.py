# Generated by Django 3.1.2 on 2020-10-17 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_auto_20201016_0852'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='payment_mode',
            field=models.IntegerField(choices=[(1, 'Card'), (2, 'Cash')], default=2),
        ),
    ]
