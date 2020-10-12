from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from authentication.forms import ShopForm
from dashboard.forms import EditUserForm, ServiceForm, ShopEditForm
from dashboard.models import Service, ServiceImage, Booking


def home(request):
    return redirect(shop_bookings)


@login_required(login_url='login')
def shop_bookings(request):
    if request.method == "POST":
        booking = Booking.objects.get(id=request.POST["id"], shop = request.user.shop)

    
        if 'accept' in request.POST:
            print("ACCEPT")
            booking.status = Booking.ACCEPTED
            booking.save()
        
        if 'decline' in request.POST:
            booking.status = Booking.DECLINED
            booking.save()
    
    booking = Booking.objects.filter(shop = request.user.shop).order_by("-id")
    return render(request, 'db/bookings.html', { "booking":booking })


@login_required(login_url='login')
def shop_account(request):
    user_form = EditUserForm(instance = request.user)
    barber_form = ShopForm(instance = request.user.shop)
    token = request.user.shop.token
  
    if request.method == "POST":
        user_form = EditUserForm(request.POST, instance=request.user)
        barber_form1 = ShopEditForm(request.POST, request.FILES, instance=request.user.shop)
        token = request.POST.get('token')
        barber_form1.token = token
        

        if user_form.is_valid() and barber_form1.is_valid():
            user_form.save()
            barber_form1.save()
    
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
        print("DELETE")
        print(delete)

        if delete=="true":
            print("CALL")
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
    return render(request, 'db/reports.html')


@login_required(login_url='login')
def shop_employees(request):
    return render(request, 'db/employees.html')

