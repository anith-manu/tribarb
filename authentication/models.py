import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Shop(models.Model):
	#id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	token = models.CharField(max_length=500, blank=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop')
	name = models.CharField(max_length=500, blank=False)
	phone = models.CharField(max_length=500, blank=False)
	address = models.CharField(max_length=500, blank=False)
	instagram = models.CharField(max_length=500, blank = True, null = False, default="")
	facebook = models.CharField(max_length=500, blank = True, null = False, default="")
	logo = models.ImageField(upload_to='shop_logo/', blank=False)
	shop_bookings = models.BooleanField(default=False)
	home_bookings = models.BooleanField(default=False)
	total_rating = models.IntegerField(default=0)
	number_of_ratings = models.IntegerField(default=0)

	def __str__(self):
		return str(self.id) + " " + self.name