from django.db import models
from django.contrib.auth.models import User
from authentication.models import Shop


class Customer(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
	avatar = models.CharField(max_length=500)
	phone = models.CharField(max_length=500, blank=True)
	address = models.CharField(max_length=500, blank=True)

	def __str__(self):
		return self.user.get_full_name


class Employee(models.Model):
	shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
	first_name = models.CharField(max_length=500, blank=True)
	last_name = models.CharField(max_length=500, blank=True)
	avatar = models.CharField(max_length=500)
	phone = models.CharField(max_length=500, blank=True)

	def __str__(self):
		return self.user.get_full_name


class Service(models.Model):
	shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
	service_name = models.CharField(max_length=500)
	short_description = models.CharField(max_length=500, blank=True)
	price = models.IntegerField(default=0)

	def __str__(self):
		return self.service_name


class ServiceImage(models.Model):
	service = models.ForeignKey(Service, on_delete=models.CASCADE, default=None)
	image = models.ImageField(upload_to='haircut_images/', blank=True)

	def __str__(self):
		return self.service.service_name

