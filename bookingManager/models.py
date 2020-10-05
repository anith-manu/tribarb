from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Shop(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop')
    name = models.CharField(max_length=500)
    phone = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    logo = models.ImageField(upload_to='shop_logo/', blank=False)
    membership_active = models.BooleanField(default=False)
    membership_expiry = models.DateField(blank = True, null = True)

    def __str__(self):
        return self.name