# Generated by Django 3.1.3 on 2020-11-17 08:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
        ('dashboard', '0003_auto_20201117_0700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.shop'),
        ),
    ]
