from django import forms
from django.contrib.auth.models import User
from authentication.models import Shop
from dashboard.models import Service, ServiceImage


class EditUserForm(forms.ModelForm):
	email = forms.CharField(max_length=100, required=True)
	
	class Meta:
		model = User
		fields = ("first_name", "last_name", "email")


class ServiceForm(forms.ModelForm):
	class Meta:
		model = Service
		exclude = ("shop",)







