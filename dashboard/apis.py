import json
from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from oauth2_provider.models import AccessToken

from authentication.models import Shop
from dashboard.models import Service, ServiceImage, Customer, Employee, Booking, BookingDetail	

from dashboard.serializers import ShopSerializerCustomer, ShopSerializerEmployee, ServiceSerializer, ServiceImageSerializer, BookingSerializer


###### CUSTOMERS ######
def customer_get_shops(request):
    shops = ShopSerializerCustomer(
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
        if Booking.objects.filter(customer = customer).exclude(status__in = [Booking.COMPLETED, Booking.DECLINED]):
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
                    payment_mode = request.POST["payment_mode"],
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



def customer_employee_location(request):

    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())

    customer = access_token.user.customer

    # Get driver's location related to this customer's current order.
    current_booking = Booking.objects.filter(customer = customer, status = Booking.ONTHEWAY).last()
    location = current_booking.employee.location

    return JsonResponse({"location": location})





###### EMPLOYEES ######
def employee_get_shop(request, shop_id):
    shop = ShopSerializerEmployee(
        Shop.objects.filter(id = shop_id),
        many = True,
        context = {"request": request}
    ).data
    
    return JsonResponse({"shop": shop})


def employee_get_placed_bookings(request, shop_id):
    bookings = BookingSerializer(
        Booking.objects.filter(shop_id = shop_id, status = Booking.PLACED, employee = None).order_by("-id"),
        many = True
    ).data

    return JsonResponse({"bookings": bookings})




@csrf_exempt
def employee_accept_booking(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
		expires__gt = timezone.now())

        employee = access_token.user.employee
      
        try:
            booking = Booking.objects.get(
                id = request.POST["booking_id"],
                employee = None,
                status = Booking.PLACED
            )
            booking.employee = employee
            booking.status = Booking.ACCEPTED
            booking.accepted_at = timezone.now()
            booking.save()

            return JsonResponse({"status": "success"})

        except Booking.DoesNotExist:
            return JsonResponse({"status": "failed", "error": "This booking has already been accepted."})
    


@csrf_exempt
def employee_decline_booking(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
		expires__gt = timezone.now())

        employee = access_token.user.employee 

        try:
            booking = Booking.objects.get(
                id = request.POST["booking_id"],
            )
            booking.employee = employee
            booking.status = Booking.DECLINED
            booking.save()

            return JsonResponse({"status": "success"})

        except Booking.DoesNotExist:
            return JsonResponse({"status": "failed", "error": "This booking has already been declined."})




@csrf_exempt
def employee_enroute(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
		expires__gt = timezone.now())

        employee = access_token.user.employee

        try:
            booking = Booking.objects.get(
                id = request.POST["booking_id"],
                status = Booking.ACCEPTED,
                booking_type = 1,
            )

            booking.status = Booking.ONTHEWAY
            booking.save()

            return JsonResponse({"status": "success"})

        except Booking.DoesNotExist:
            return JsonResponse({"status": "failed", "error": "This booking has been accepted by another barber."})
    



@csrf_exempt
def employee_complete_booking(request):
    access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
        expires__gt = timezone.now())

    employee = access_token.user.employee

    booking = Booking.objects.get(id = request.POST["booking_id"], employee = employee)
    booking.status = Booking.COMPLETED
    booking.save()

    return JsonResponse({"status": "success"})
    



def employee_get_booking_info(request, booking_id):
    booking = BookingSerializer(
        Booking.objects.filter(id = booking_id),
        many = True,
        context = {"request": request}
    ).data

    return JsonResponse({"booking": booking})




def employee_get_revenue(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())

    employee = access_token.user.employee

    from datetime import timedelta

    revenue = {}
    today = timezone.now()
    current_weekdays = [today + timedelta(days = i) for i in range(0 - today.weekday(), 7 - today.weekday())]

    for day in current_weekdays:
        bookings = Booking.objects.filter(
            employee = employee,
            status = Booking.COMPLETED,
            created_at__year = day.year,
            created_at__month = day.month,
            created_at__day = day.day
        )

        revenue[day.strftime("%a")] = sum(booking.total for booking in bookings)

    return JsonResponse({"revenue": revenue})



@csrf_exempt
def employee_update_location(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())

        employee = access_token.user.employee

        # Set location string => database
        employee.location = request.POST["location"]
        employee.save()

        return JsonResponse({"status": "success"})




###### NOTIFICATION ######
def shop_booking_notification(request, last_request_time):
    #notification = Booking.objects.filter(shop = request.user.shop,
     #   created_at__gt = last_request_time).count()
    
    notification = Booking.objects.filter(shop = request.user.shop, status=1).count()


    return JsonResponse({"notification": notification})