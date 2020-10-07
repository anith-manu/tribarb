from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.decorators import login_required


def home(request):
    return redirect(shop_bookings)

@login_required(login_url='login')
def shop_bookings(request):
    return render(request, 'db/bookings.html')

