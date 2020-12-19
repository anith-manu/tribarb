import json
from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from oauth2_provider.models import AccessToken

from authentication.models import Shop
from dashboard.models import Service, ServiceImage, Customer, Employee, Booking, BookingDetail	

from dashboard.serializers import ShopSerializerCustomer, ShopSerializerEmployee, ServiceSerializer, ServiceImageSerializer, BookingSerializer, CustomerSerializer, EmployeeSerializer

import stripe
from tribarbDesktop.settings import STRIPE_API_KEY

from pusher_push_notifications import PushNotifications



beams_client = PushNotifications(
    instance_id='e4ca64ad-a6d3-41af-b291-f7b39f7f9ba2',
    secret_key='52E27A28876BD39A437CA40C15F49C443827BE6EEA1967305D5F515FED57B127',
)

stripe.api_key = STRIPE_API_KEY

STRIPE_CUSTOMER = ""

###### CUSTOMERS ######
@csrf_exempt
def stripe_ephemeral_key(request):
    """Returns ephemeral key
    """
    # Get token
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
		expires__gt = timezone.now())

    # Get profile
    customer = access_token.user.customer

    customer_stripe_id = customer.stripe_id
    api_version = request.GET.get("api_version")

    data = stripe.EphemeralKey.create(customer=customer_stripe_id, stripe_version=api_version)

    return JsonResponse(data)


def customer_get_shops(request, filter_id):
    if filter_id == 0:
        filter_shops = Shop.objects.filter(shop_bookings=True, visible_on_app=True)
    else:
        filter_shops =  Shop.objects.filter(home_bookings=True, visible_on_app=True)
    
    shops = ShopSerializerCustomer(
        filter_shops.order_by("-id"),
        many = True,
        context = {"request": request}
    ).data

    return JsonResponse({"shops": shops})


def customer_get_services(request, filter_id, shop_id):
    if filter_id == 0:
        filter_services = Service.objects.filter(shop_id = shop_id, shop_service=True)
    else:
        filter_services = Service.objects.filter(shop_id = shop_id, home_service=True)

    services = ServiceSerializer(
        filter_services.order_by("-id"),
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



def get_stripe_client_secret(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
            expires__gt = timezone.now())

    booking_total = request.GET["total"]
   
    customer = access_token.user.customer

    intent = stripe.PaymentIntent.create(
        amount = int(float(booking_total)*100),
        currency='gbp',
        customer = customer.stripe_id,
        description = "Tribarb Booking",
        )

    client_secret = intent.client_secret 

    return JsonResponse({"clientSecret": client_secret})




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

        # Check Address	
        if request.POST["booking_type"] == "1":
            if not request.POST["address"]:
                return JsonResponse({"status": "failed", "error": "Address is required."})


        # Get Booking Details   
        booking_details = json.loads(request.POST["booking_details"])

        booking_subtotal = float(request.POST["subtotal"])
        booking_service_fee = float(request.POST["service_fee"])
        booking_total = float(request.POST["total"])

        if len(booking_details) > 0:
    
            booking = Booking.objects.create(
                    customer = customer,
                    shop_id = request.POST["shop_id"],
                    booking_type = request.POST["booking_type"],
                    payment_mode = request.POST["payment_mode"],
                    requests = request.POST["requests"],
                    requested_time = request.POST["requested_time"],
                    total = booking_total,
                    service_fee = booking_service_fee,
                    subtotal = booking_subtotal,
                    status = Booking.PLACED,
                    address = request.POST["address"],
                )
            
            
            for service in booking_details:
                BookingDetail.objects.create(
                        booking = booking,
                        service_id = service["service_id"]
                    )
                    
       
            return JsonResponse({"status": "success"})
      



def customer_get_latest_booking(request):
	access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
		expires__gt = timezone.now())

	customer = access_token.user.customer
	booking = BookingSerializer(Booking.objects.filter(customer = customer).last()).data

	return JsonResponse({"booking": booking})



def customer_get_bookings(request, filter_id):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
            expires__gt = timezone.now())
    
    customer = access_token.user.customer

    if filter_id == 0 :
        bookings = BookingSerializer(
            Booking.objects.filter(customer = customer, status__in=[1, 2, 3]).order_by("requested_time"),
            many = True
        ).data
    
    else :
        bookings = BookingSerializer(
            Booking.objects.filter(customer = customer, status__in=[4, 5, 6]).order_by("requested_time"),
            many = True
        ).data


    return JsonResponse({"bookings": bookings})



def get_booking(request, booking_id):
	access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
		expires__gt = timezone.now())

	booking = BookingSerializer(
        Booking.objects.get(id=booking_id)
        ).data

	return JsonResponse({"booking": booking})


def customer_employee_location(request):

    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())

    customer = access_token.user.customer

    # Get driver's location related to this customer's current order.
    current_booking = Booking.objects.filter(customer = customer, status = Booking.ONTHEWAY).last()
    location = current_booking.employee.location

    return JsonResponse({"location": location})


@csrf_exempt
def customer_cancel_booking(request, booking_id):

    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())
            
        customer = access_token.user.customer
        
        booking = Booking.objects.get(id=booking_id, customer = customer)

        if booking.status == booking.PLACED:
            booking.status = booking.CANCELLED
            booking.save()
            return JsonResponse({"status": "success"})
        else :
            return JsonResponse({"status": "failed. The booking has already been accepted."})

    

@csrf_exempt
def customer_update_details(request):

    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())
            
        customer = access_token.user.customer
        
        customer.phone = request.POST["phone"]
        customer.address = request.POST["address"]
        customer.save()

        return JsonResponse({"status": "success"})
        


def customer_get_details(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
		expires__gt = timezone.now())
        
    customer = access_token.user.customer

    customerInfo = CustomerSerializer(
        customer
        ).data

    return JsonResponse({"customer": customerInfo})




@csrf_exempt
def customer_update_ratings(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())
        
        if access_token != "" :
            booking = Booking.objects.get(id = request.POST["booking_id"])
            booking.rating = request.POST["rating"]
            booking.save()

            shop = booking.shop
            shop.total_rating = shop.total_rating + int(request.POST["rating"])
            shop.number_of_ratings = shop.number_of_ratings + 1
            shop.save()   
            
            return JsonResponse({"status": "success"})  
  



###### EMPLOYEES ######
def employee_get_details(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
		expires__gt = timezone.now())
        
    employee = access_token.user.employee

    employeeInfo = EmployeeSerializer(
        employee
        ).data

    return JsonResponse({"employee": employeeInfo})



@csrf_exempt
def employee_update_details(request):

    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())
            
        employee = access_token.user.employee
        
        employee.phone = request.POST["phone"]
        employee.save()

        return JsonResponse({"status": "success"})


    
@csrf_exempt
def employee_verify(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())
        
        employee = access_token.user.employee

        shop = Shop.objects.get(id = request.POST["shop_id"])
        shop_token = shop.token
        token = request.POST["token"]

        if shop_token == token:
            employee.shop = shop
            employee.save()
            return JsonResponse({"status": "success"})  
        else:
            return JsonResponse({"status": "failed"})  






def employee_get_bookings(request, filter_id):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
            expires__gt = timezone.now())

    employee = access_token.user.employee
    shop = employee.shop

    if filter_id == 0 :
        bookings = BookingSerializer(
            Booking.objects.filter(shop = shop, status = Booking.PLACED).order_by("requested_time"),
            many = True
        ).data

    elif filter_id == 1 :
        bookings = BookingSerializer(
            Booking.objects.filter(shop = shop, status__in=[2, 3]).order_by("requested_time"),
            many = True
        ).data
    
    else :
        bookings = BookingSerializer(
            Booking.objects.filter(shop = shop, status__in=[4, 5, 6]).order_by("requested_time"),
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
                status = Booking.PLACED
            )
            booking.employee = employee
            booking.status = Booking.ACCEPTED
            booking.accepted_at = timezone.now()
            booking.save()


          


            response = beams_client.publish_to_interests(
                interests=['hello'],
                publish_body={
                    'apns': {
                        'aps': {
                            'alert': {
                                'title': "Your booking from %s has been accepted"% (booking.shop.name),
                                'body': "Your barber is %s "% (booking.employee)
                            }
                        }
                    }
                }
            )

            print(response['publishId'])

            return JsonResponse({"status": "success"})

        except Booking.DoesNotExist:
            return JsonResponse({"status": "failed", "error": "Someone else has already responded to this booking."})
    


@csrf_exempt
def employee_decline_booking(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
		expires__gt = timezone.now())

        employee = access_token.user.employee 

        try:
            booking = Booking.objects.get(
                id = request.POST["booking_id"]
            )
            booking.employee = employee
            booking.status = Booking.DECLINED
            booking.save()

            return JsonResponse({"status": "success"})

        except Booking.DoesNotExist:
            return JsonResponse({"status": "failed", "error": "Someone else has already responded to this booking."})




@csrf_exempt
def employee_enroute(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
		expires__gt = timezone.now())

        employee = access_token.user.employee

        try:
            booking = Booking.objects.get(
                id = request.POST["booking_id"],
                status = Booking.ACCEPTED
            )
            booking.employee = employee
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

    try:
        booking = Booking.objects.get(
            id = request.POST["booking_id"]
        )
        booking.employee = employee
        booking.status = Booking.COMPLETED
        booking.save()

        return JsonResponse({"status": "success"})

    except Booking.DoesNotExist:
        return JsonResponse({"status": "failed", "error": "This booking has been accepted by another barber."})


    



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




def check_user_last_loggin_in_as(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
            expires__gt = timezone.now())


    user = access_token.user 

    user_is_customer = Customer.objects.filter(user=user).count()
    user_is_employee = Employee.objects.filter(user=user).count()

    if user_is_customer > 0:
        last_logged_in_as_customer =  Customer.objects.get(user=user).last_logged_in_as
        if last_logged_in_as_customer == True:
            return JsonResponse({"last_logged_in_as": "customer"})
    
    if user_is_employee > 0:
        last_logged_in_as_employee =  Employee.objects.get(user=user).last_logged_in_as

        if last_logged_in_as_employee == True:
            verified = False

            if Employee.objects.get(user=user).shop != None:
                verified = True

            return JsonResponse({"last_logged_in_as": "employee", "verified": verified})
        
    


@csrf_exempt
def set_user_last_loggin_in_as(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())

        user = access_token.user 

        user_is_customer = Customer.objects.filter(user=user).count()
        user_is_employee = Employee.objects.filter(user=user).count()


        if request.POST["user_type"] == "customer":
            customer = user.customer
            customer.last_logged_in_as = True
            customer.save()

            if user_is_employee > 0:
                employee = user.employee
                employee.last_logged_in_as = False
                employee.save()
            
            return JsonResponse({"status": "success"})


        if request.POST["user_type"] == "employee":
            employee = user.employee
            employee.last_logged_in_as = True
            employee.save()
            
            if user_is_customer > 0:
                customer = user.customer
                customer.last_logged_in_as = False
                customer.save()

            return JsonResponse({"status": "success"})



    