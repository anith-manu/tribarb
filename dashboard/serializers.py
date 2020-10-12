from rest_framework import serializers

from authentication.models import Shop
from dashboard.models import Service, Customer, Employee, Booking, BookingDetail	



class ShopSerializer(serializers.ModelSerializer):
	logo = serializers.SerializerMethodField()

	def get_logo(self, barber):
	    request = self.context.get('request')
	    logo_url = barber.logo.url
	    return request.build_absolute_uri(logo_url)

	class Meta:
	    model = Shop
	    fields = ("id", "name", "phone", "address", "logo")