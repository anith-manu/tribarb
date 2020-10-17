from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from authentication.forms import ShopForm
from dashboard.forms import EditUserForm, ServiceForm
from dashboard.models import Service, ServiceImage, Booking, Employee

from django.db.models import Sum, Count, Case, When

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
    return render(request, 'db/bookings.html', { "booking":booking })


@login_required(login_url='login')
def shop_bookings_completed(request):
    booking = Booking.objects.filter(shop = request.user.shop).order_by("-id")
    return render(request, 'db/bookings_completed.html', { "booking":booking })


@login_required(login_url='login')
def shop_account(request):
    user_form = EditUserForm(instance = request.user)
    barber_form = ShopForm(instance = request.user.shop)
    token = request.user.shop.token
  
    if request.method == "POST":
        user_form = EditUserForm(request.POST, instance=request.user)
        barber_form = ShopForm(request.POST, request.FILES, instance=request.user.shop)
        token = request.POST.get('token')
        request.user.shop.token = token
        
        if user_form.is_valid() and barber_form.is_valid():
            user_form.save()
            barber_form.save()
        
    ## Bug here with barber form. Changes do not get updated immediately in template. 
    return render(request, 'db/account.html', {
		"user_form": user_form,
		"barber_form": barber_form,
        "token": token
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

        post = Service.objects.create(
            shop = request.user.shop,
            service_name=title,
            short_description=description,
            price=price
        )
        
        for file_num in range(0, int(length)):
            ServiceImage.objects.create(
                service=post,
                image=request.FILES.get(f'images{file_num}')
            )
    
    return render(request, 'db/add_services.html')
    



@login_required(login_url='/barber/sign-in/')
def shop_edit_services(request, service_id):   

    service = Service.objects.get(id=service_id)
    
    
    if request.method == 'POST':
        service = Service.objects.get(id=service_id)

        delete =  request.POST.get('delete')

        if delete=="true":
            service.delete()
        else:
            service.service_name = request.POST.get('service_name')
            service.short_description = request.POST.get('short_description')
            service.price = request.POST.get('price')
            albumUpdate = request.POST.get('albumUpdate')

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
                     .annotate(total_booking = Sum('bookingdetail__sub_total'))\
                     .order_by("-total_booking")

    service = {
        "labels": [service.service_name for service in top_services],
        "data": [service.total_booking or 0 for service in top_services]
    }

    # Top 3 Drivers
    top_employees = Employee.objects.annotate(
        total_booking = Count(
            Case (
                When(booking__shop = request.user.shop, then = 1)
            )
        )
    ).order_by("-total_booking")

    employee = {
        "labels": [employee.first_name for employee in top_employees],
        "data": [employee.total_booking for employee in top_employees]
    }

    return render(request, 'db/reports.html', {
    "revenue": revenue,
    "bookings": bookings,
    "service": service,
    "employee": employee
})



@login_required(login_url='login')
def shop_employees(request):
    employees = Employee.objects.filter(shop = request.user.shop).order_by("id")
    return render(request, 'db/employees.html', {"employees":employees})

