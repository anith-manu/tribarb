from django.db import models
from django.contrib.auth.models import User
from authentication.models import Shop
from django.utils import timezone


class Customer(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
	avatar = models.CharField(max_length=500, default="")
	email = models.CharField(max_length=500, default="")
	stripe_id = models.CharField(max_length=500, default="")
	phone = models.CharField(max_length=500, default="")
	address = models.CharField(max_length=500, blank = True, default="")
	last_logged_in_as = models.BooleanField(default=False)

	def __str__(self):
		return str(self.id) + " " + self.user.get_full_name()


class Employee(models.Model):
	shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True, blank=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
	email = models.CharField(max_length=500, default="")
	phone = models.CharField(max_length=500, default="")
	avatar = models.CharField(max_length=500, blank = True, default="")
	location = models.CharField(max_length=500, blank = True, default="")
	last_logged_in_as = models.BooleanField(default=False)

	def __str__(self):
		return str(self.id) + " " + self.user.get_full_name() 


class Service(models.Model):
	shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
	service_name = models.CharField(max_length=500, default="")
	short_description = models.CharField(max_length=500, blank = True, default="")
	price = models.FloatField(default=0)
	shop_service = models.BooleanField(default=False)
	home_service = models.BooleanField(default=False)

	def __str__(self):
		return str(self.id) + " " + self.service_name


class ServiceImage(models.Model):
	service = models.ForeignKey(Service, on_delete=models.CASCADE, default=None)
	image = models.ImageField(upload_to='service_images/', blank=True)

	def __str__(self):
		return self.service.service_name



class Booking(models.Model):
	PLACED = 1
	ACCEPTED = 2
	ONTHEWAY = 3
	COMPLETED = 4
	DECLINED = 5
	CANCELLED = 6

	SHOP_BOOKING = 0
	HOME_BOOKING = 1
	
	CASH = 0
	CARD = 1
	

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


	PAYMENT_MODE = (
		(CARD, "Card"),
        (CASH, "Cash"),
    )


	booking_type = models.IntegerField(choices = BOOKING_CHOICES, default = SHOP_BOOKING)
	payment_mode = models.IntegerField(choices = PAYMENT_MODE, default = CASH)
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
	employee = models.ForeignKey(Employee, null = True, on_delete=models.CASCADE)
	status = models.IntegerField(choices = STATUS_CHOICES)
	created_at = models.DateTimeField(default = timezone.now)
	requested_time = models.DateTimeField(blank = True, null = True)
	address = models.CharField(max_length=500, blank = True, null = True, default="")
	requests = models.CharField(max_length=500, blank = True, default="")
	accepted_at = models.DateTimeField(blank = True, null = True)
	rating = models.IntegerField(blank=True, default=0)
	service_fee = models.FloatField(default=0)
	subtotal = models.FloatField(default=0)
	total = models.FloatField(default=0)

	def __str__(self):
	    return str(self.id)


class BookingDetail(models.Model):
	booking = models.ForeignKey(Booking, related_name='booking_details', on_delete=models.CASCADE)
	service = models.ForeignKey(Service, on_delete=models.CASCADE)

	def __str__(self):
	    return str(self.id)