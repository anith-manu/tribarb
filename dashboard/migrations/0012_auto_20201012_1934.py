# Generated by Django 3.1.2 on 2020-10-12 19:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_auto_20201011_2014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.employee'),
        ),
    ]
