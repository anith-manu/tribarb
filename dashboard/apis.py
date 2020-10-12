import json

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from oauth2_provider.models import AccessToken

from authentication.models import Shop
from dashboard.models import Service, Customer, Employee, Booking, BookingDetail	

from dashboard.serializers import ShopSerializer


def customer_get_shops(request):
	shops = ShopSerializer(
	    Shop.objects.all().order_by("-id"),
	    many = True,
	    context = {"request": request}
	).data

	return JsonResponse({"shops": shops})