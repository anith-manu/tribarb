from django.db import models
from django.contrib.auth.models import User
from authentication.models import Shop
from django.utils import timezone


class Customer(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
	avatar = models.CharField(max_length=500)
	phone = models.CharField(max_length=500, blank=True)
	address = models.CharField(max_length=500, blank=True)

	def __str__(self):
		return self.user.get_full_name()


class Employee(models.Model):
	shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
	first_name = models.CharField(max_length=500, blank=True)
	last_name = models.CharField(max_length=500, blank=True)
	avatar = models.CharField(max_length=500)
	phone = models.CharField(max_length=500, blank=True)

	def __str__(self):
		return self.user.get_full_name() 


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



class Booking(models.Model):
	PLACED = 1
	ACCEPTED = 2
	ONTHEWAY = 3
	COMPLETED = 4
	DECLINED = 5
	CANCELLED = 6

	HOME_BOOKING = 1
	SHOP_BOOKING = 2

	STATUS_CHOICES = (
		(PLACED, "Placed"),
        (ACCEPTED, "Accepted"),
        (ONTHEWAY, "Barber En Route"),
        (COMPLETED, "Completed"),
		(DECLINED, "Declined"),
		(CANCELLED, "Cancelled"),
    )

	BOOKING_CHOICES = (
		(HOME_BOOKING, "Home"),
        (SHOP_BOOKING, "Shop"),
    )

	booking_type = models.IntegerField(choices = BOOKING_CHOICES, default = SHOP_BOOKING)
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
	employee = models.ForeignKey(Employee, blank = True, on_delete=models.CASCADE)
	address = models.CharField(max_length=500, blank = True, null = True)
	total = models.FloatField()
	status = models.IntegerField(choices = STATUS_CHOICES)
	created_at = models.DateTimeField(default = timezone.now)
	requested_time = models.DateTimeField(blank = True, null = True)
	accepted_at = models.DateTimeField(blank = True, null = True)

	def __str__(self):
	    return str(self.id)


class BookingDetail(models.Model):
	booking = models.ForeignKey(Booking, related_name='booking_details', on_delete=models.CASCADE)
	service = models.ForeignKey(Service, on_delete=models.CASCADE)
	sub_total = models.FloatField()

	def __str__(self):
	    return str(self.id)