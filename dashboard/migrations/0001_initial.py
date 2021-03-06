# Generated by Django 3.1.2 on 2020-10-18 16:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_type', models.IntegerField(choices=[(1, 'Home'), (2, 'Shop')], default=2)),
                ('payment_mode', models.IntegerField(choices=[(1, 'Card'), (2, 'Cash')], default=2)),
                ('address', models.CharField(blank=True, max_length=500, null=True)),
                ('total', models.FloatField()),
                ('status', models.IntegerField(choices=[(1, 'Placed'), (2, 'Accepted'), (3, 'Barber En Route'), (4, 'Completed'), (5, 'Declined'), (6, 'Cancelled')])),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('requested_time', models.DateTimeField(blank=True, null=True)),
                ('requests', models.CharField(blank=True, max_length=500, null=True)),
                ('accepted_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(max_length=500)),
                ('short_description', models.CharField(blank=True, max_length=500)),
                ('price', models.FloatField(default=0)),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.shop')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, upload_to='haircut_images/')),
                ('service', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='dashboard.service')),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=500)),
                ('last_name', models.CharField(blank=True, max_length=500)),
                ('avatar', models.CharField(max_length=500)),
                ('phone', models.CharField(blank=True, max_length=500)),
                ('address', models.CharField(blank=True, max_length=500)),
                ('location', models.CharField(blank=True, max_length=500)),
                ('shop', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.shop')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='employee', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.CharField(max_length=500)),
                ('phone', models.CharField(blank=True, max_length=500)),
                ('address', models.CharField(blank=True, max_length=500)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='customer', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BookingDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_total', models.FloatField()),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booking_details', to='dashboard.booking')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.service')),
            ],
        ),
        migrations.AddField(
            model_name='booking',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.customer'),
        ),
        migrations.AddField(
            model_name='booking',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.employee'),
        ),
        migrations.AddField(
            model_name='booking',
            name='shop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.shop'),
        ),
    ]
