from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from authentication.forms import ShopForm
from dashboard.forms import EditUserForm


def home(request):
    return redirect(shop_bookings)

@login_required(login_url='login')
def shop_bookings(request):
    return render(request, 'db/bookings.html')


@login_required(login_url='login')
def shop_account(request):
    user_form = EditUserForm(instance = request.user)
    barber_form = ShopForm(instance = request.user.shop)

    if request.method == "POST":
        user_form = EditUserForm(request.POST, instance=request.user)
        barber_form = ShopForm(request.POST, request.FILES, instance=request.user.shop)

        if user_form.is_valid() and barber_form.is_valid():
            user_form.save()
            barber_form.save()
    
    return render(request, 'db/account.html', {
		"user_form": user_form,
		"barber_form": barber_form
		})


@login_required(login_url='login')
def shop_services(request):
    return render(request, 'db/services.html')


@login_required(login_url='login')
def shop_reports(request):
    return render(request, 'db/reports.html')


@login_required(login_url='login')
def shop_employees(request):
    return render(request, 'db/employees.html')

