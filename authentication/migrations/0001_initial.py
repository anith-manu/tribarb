# Generated by Django 3.1.3 on 2020-11-13 13:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(blank=True, max_length=500)),
                ('name', models.CharField(max_length=500)),
                ('phone', models.CharField(max_length=500)),
                ('address', models.CharField(max_length=500)),
                ('instagram', models.CharField(blank=True, default='', max_length=500)),
                ('facebook', models.CharField(blank=True, default='', max_length=500)),
                ('logo', models.ImageField(upload_to='shop_logo/')),
                ('shop_bookings', models.BooleanField(default=False)),
                ('home_bookings', models.BooleanField(default=False)),
                ('total_rating', models.IntegerField(default=0)),
                ('number_of_ratings', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='shop', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
