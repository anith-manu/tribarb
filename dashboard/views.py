from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from authentication.forms import ShopForm
from dashboard.forms import EditUserForm, ServiceForm
from dashboard.models import Service, ServiceImage, Booking, Employee
from django.db.models import Sum, Count, Case, When
from django.conf import settings

def home(request):
    return redirect(shop_bookings)


@login_required(login_url='login')
def shop_bookings(request):
    if request.method == "POST":
        booking = Booking.objects.get(id=request.POST["id"], shop = request.user.shop)

    
        if 'accept' in request.POST:
            booking.status = Booking.ACCEPTED
            booking.save()
        
        if 'decline' in request.POST:
            booking.status = Booking.DECLINED
            booking.save()
    
    booking = Booking.objects.filter(shop = request.user.shop).order_by("-id")
    return render(request, 'db/bookings.html', { "bookings":booking })


@login_required(login_url='login')
def shop_bookings_completed(request):
    booking = Booking.objects.filter(shop = request.user.shop).order_by("-id")
    return render(request, 'db/bookings_completed.html', { "booking":booking })




@login_required(login_url='login')
def shop_employees(request):
    if request.method == "POST":
        employee = Employee.objects.get(id=request.POST["id"])

        employee.shop = None
        employee.save()
            
    employees = Employee.objects.filter(shop = request.user.shop).order_by("id")
    return render(request, 'db/employees.html', {"employees":employees})


@login_required(login_url='login')
def shop_account(request):
    user_form = EditUserForm(instance = request.user)
    shop_form = ShopForm(instance = request.user.shop)

    if request.method == "POST":
        user_form = EditUserForm(request.POST, instance=request.user)
        shop_form = ShopForm(request.POST, request.FILES, instance=request.user.shop)
        token = request.POST.get('token')
        instagram = request.POST.get('instagram')
        facebook = request.POST.get('facebook')

        if 'visibility' in request.POST:
            request.user.shop.visible_on_app = True
        else:
            request.user.shop.visible_on_app = False

        request.user.shop.token = token
        request.user.shop.instagram = instagram
        request.user.shop.facebook = facebook
        
        if user_form.is_valid() and shop_form.is_valid():
            user_form.save()
            shop_form.save()
        
    ## Bug here with barber form. Changes do not get updated immediately in template. 
    return render(request, 'db/account.html', {
		"user_form": user_form,
		"shop_form": shop_form,
        "mapsKey" : settings.GOOGLE_MAPS_API_KEY,
		})


@login_required(login_url='login')
def shop_services(request):
    services = Service.objects.filter(shop = request.user.shop).order_by("id")
    return render(request, 'db/services.html', {"services":services})



@login_required(login_url='login')
def shop_add_services(request):
    if request.method == 'POST':
        length = request.POST.get('length')
        title = request.POST.get('service_name')
        description = request.POST.get('short_description')
        price = request.POST.get('price')
        shopService = request.POST.get('shopService')
        homeService = request.POST.get('homeService')
        shop = False
        home = False

        if shopService == "shop":
            shop = True
        
        if homeService == "home":
            home = True

        post = Service.objects.create(
            shop = request.user.shop,
            service_name=title,
            short_description=description,
            price=price,
            shop_service=shop,
            home_service=home
        )
        
        for file_num in range(0, int(length)):
            ServiceImage.objects.create(
                service=post,
                image=request.FILES.get(f'images{file_num}')
            )
    
    return render(request, 'db/add_services.html')
    
    

@login_required(login_url='/barber/sign-in/')
def shop_view_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    return render(request, 'db/booking.html', {
        "booking":booking
        })



@login_required(login_url='/barber/sign-in/')
def shop_edit_services(request, service_id):   

    service = Service.objects.get(id=service_id)
    
    
    if request.method == 'POST':
        service = Service.objects.get(id=service_id)

        delete =  request.POST.get('delete')

        if delete=="true":
            service.delete()
        else:

            if request.POST.get('service_name') == "":
                return render(request, 'db/edit_services.html', {
                    "service":service
                })


            service.service_name = request.POST.get('service_name')
            service.short_description = request.POST.get('short_description')
            service.price = request.POST.get('price')
            albumUpdate = request.POST.get('albumUpdate')
            shopService = request.POST.get('shopService')
            homeService = request.POST.get('homeService')
            shop = False
            home = False


            if shopService == "shop":
                shop = True
        
            if homeService == "home":
                home = True
            
            service.shop_service = shop
            service.home_service = home

            if albumUpdate == "create":
                ServiceImage.objects.filter(service=service).delete()

            length = request.POST.get('length')

            for file_num in range(0, int(length)):
                ServiceImage.objects.create(
                    service=service,
                    image=request.FILES.get(f'images{file_num}')
                )
            service.save()

    return render(request, 'db/edit_services.html', {
        "service":service
        })







@login_required(login_url='/barber/sign-in/')
def shop_service_album(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    photos = ServiceImage.objects.filter(service = service)

    return render(request, 'db/service_album.html', {
        "service": service,
        "photos": photos,
    })




@login_required(login_url='login')
def shop_reports(request):
    # Calculate revenue and number of order by current week
    from datetime import datetime, timedelta

    revenue = []
    bookings = []

    # Calculate weekdays
    today = datetime.now()
    current_weekdays = [today + timedelta(days = i) for i in range(0 - today.weekday(), 7 - today.weekday())]

    for day in current_weekdays:
        completed_bookings = Booking.objects.filter(
            shop = request.user.shop,
            status = Booking.COMPLETED,
            created_at__year = day.year,
            created_at__month = day.month,
            created_at__day = day.day
        )
        revenue.append(sum(booking.total for booking in completed_bookings))
        bookings.append(completed_bookings.count())

    # Top 3 Meals
    top_services = Service.objects.filter(shop = request.user.shop)\
                     .annotate(total_booking = Sum('bookingdetail__service__price'))\
                     .order_by("-total_booking")

    service = {
        "labels": [service.service_name for service in top_services],
        "data": [service.total_booking or 0 for service in top_services]
    }


    # Top 3 Employees
    top_employees = Employee.objects.annotate(
        total_booking = Count(
            Case (
                When(booking__shop = request.user.shop, then = 1)
            )
        )
    ).order_by("-total_booking")
    

    employee = {
        "labels": [employee.user.get_short_name() for employee in top_employees],
        "data": [employee.total_booking for employee in top_employees]
    }

    print("Revenue")
    print(revenue)
        
    return render(request, 'db/reports.html', {
    "revenue": revenue,
    "bookings": bookings,
    "service": service,
    "employee": employee
})




