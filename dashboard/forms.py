from django import forms
from django.contrib.auth.models import User
from authentication.models import Shop


class EditUserForm(forms.ModelForm):
	email = forms.CharField(max_length=100, required=True)
	
	class Meta:
		model = User
		fields = ("first_name", "last_name", "email")