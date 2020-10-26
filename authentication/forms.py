from django import forms
from django.contrib.auth.models import User
from authentication.models import Shop


class ShopForm(forms.ModelForm):
	name = forms.CharField(label='Shop name')

	class Meta:
		model = Shop
		fields = ("logo", "name", "phone", "address", "shop_bookings", "home_bookings")


