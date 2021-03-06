from rest_framework import serializers

from authentication.models import Shop
from dashboard.models import Service, ServiceImage, Customer, Employee, Booking, BookingDetail	



class ShopSerializerCustomer(serializers.ModelSerializer):
	logo = serializers.SerializerMethodField()

	def get_logo(self, barber):
	    request = self.context.get('request')
	    logo_url = barber.logo.url
	    return request.build_absolute_uri(logo_url)

	class Meta:
	    model = Shop
	    fields = ("id", "name", "phone", "address", "logo")



class ShopSerializerEmployee(serializers.ModelSerializer):
	logo = serializers.SerializerMethodField()

	def get_logo(self, barber):
	    request = self.context.get('request')
	    logo_url = barber.logo.url
	    return request.build_absolute_uri(logo_url)

	class Meta:
	    model = Shop
	    fields = ("id", "token", "name", "phone", "address", "logo")


class ServiceSerializer(serializers.ModelSerializer):
	# Comment this out and remove image in fields if needed
    class Meta:
        model = Service
        fields = ("id", "service_name", "short_description", "price")



class ServiceImageSerializer(serializers.ModelSerializer):
	image = serializers.SerializerMethodField()

	def get_image(self, service):
		request = self.context.get('request')
		image_url = service.image.url
		return request.build_absolute_uri(image_url)
	
	class Meta:
		model = ServiceImage
		fields = ("image",)


# BOOKING SERIALIZER
class BookingCustomerSerializer(serializers.ModelSerializer):
	name = serializers.ReadOnlyField(source="user.get_full_name")

	class Meta:
		model = Customer
		fields = ("id", "name", "avatar", "phone", "address")


class BookingEmployeeSerializer(serializers.ModelSerializer):
	name = serializers.ReadOnlyField(source="user.get_full_name")
	class Meta:
		model = Employee
		fields = ("id", "name", "avatar", "phone", "address")


class BookingShopSerializer(serializers.ModelSerializer):
	class Meta:
		model = Shop
		fields = ("id", "name", "phone", "address")


class BookingServiceSerializer(serializers.ModelSerializer):
	class Meta:
		model = Service
		fields = ("id", "service_name", "price")


class BookingDetailsSerializer(serializers.ModelSerializer):
	service = BookingServiceSerializer()

	class Meta:
		model = BookingDetail
		fields = ("id", "service", "sub_total")


class BookingSerializer(serializers.ModelSerializer):
    customer = BookingCustomerSerializer()
    employee = BookingEmployeeSerializer()
    shop = BookingShopSerializer()
    booking_details = BookingDetailsSerializer(many = True)
    status = serializers.ReadOnlyField(source = "get_status_display")

    class Meta:
        model = Booking
        fields = ("id", "customer", "booking_type", "payment_mode", "shop", "employee", "booking_details", "total", "requested_time", "requests", "status", "address")