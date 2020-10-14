import json

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from oauth2_provider.models import AccessToken

from authentication.models import Shop
from dashboard.models import Service, ServiceImage, Customer, Employee, Booking, BookingDetail	

from dashboard.serializers import ShopSerializer, ServiceSerializer, ServiceImageSerializer, BookingSerializer


def customer_get_shops(request):
    shops = ShopSerializer(
        Shop.objects.all().order_by("-id"),
        many = True,
        context = {"request": request}
    ).data

    return JsonResponse({"shops": shops})

def customer_get_services(request, shop_id):
    services = ServiceSerializer(
        Service.objects.filter(shop_id = shop_id).order_by("-id"),
        many = True,
        context = {"request": request}
    ).data

    return JsonResponse({"services": services})
    

def customer_get_service_album(request, service_id):

    album = ServiceImageSerializer(
        ServiceImage.objects.filter(service_id = service_id),
        many = True,
        context = {"request": request}
    ).data

    return JsonResponse({"album": album})



@csrf_exempt
def customer_add_booking(request):
    """
        params:
            access_token
            barber_id
            booking_type
            requested_employee
            requested_time
            address
            booking_details (json format), example:
                [{"service_id": 1},{"service_id": 2}]
            stripe_token

        return:
            {"status": "success"}
    """
    if request.method == "POST":
        # Get token
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())

        # Get profile
        customer = access_token.user.customer

        # Get Stripe token
        #stripe_token = request.POST.get("stripe_token")


        # Check whether customer has any booking that is not completed
        if Booking.objects.filter(customer = customer).exclude(status = Booking.COMPLETED):
            return JsonResponse({"status": "failed", "error": "Your last booking must be completed."})

        # Check Address	
        if request.POST["booking_type"] == "1":
            if not request.POST["address"]:
                return JsonResponse({"status": "failed", "error": "Address is required."})


        # Get Booking Details   
        booking_details = json.loads(request.POST["booking_details"])

        booking_total = 0
        for service in booking_details:
            booking_total += Service.objects.get(id = service["service_id"]).price


        if len(booking_details) > 0:
 
            booking = Booking.objects.create(
                    customer = customer,
                    shop_id = request.POST["shop_id"],
                    booking_type = request.POST["booking_type"],
                    requests = request.POST["requests"],
                    requested_time = request.POST["requested_time"],
                    total = booking_total,
                    status = Booking.PLACED,
                    address = request.POST["address"],
                )


            # Step 3 - Create Order details 
            for service in booking_details:
                BookingDetail.objects.create(
                        booking = booking,
                        service_id = service["service_id"],
                        sub_total = Service.objects.get(id = service["service_id"]).price
                    )

            return JsonResponse({"status": "success"})

        else:
            return JsonResponse({"status": "failed", "error": "Failed to connect to Stripe."})


def customer_get_latest_booking(request):
	access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
		expires__gt = timezone.now())

	customer = access_token.user.customer
	booking = BookingSerializer(Booking.objects.filter(customer = customer).last()).data

	return JsonResponse({"booking": booking})
    

def shop_booking_notification(request, last_request_time):
    notification = Booking.objects.filter(shop = request.user.shop,
        created_at__gt = last_request_time).count()

    return JsonResponse({"notification": notification})