from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
        path('', views.home, name='home'),
        path('bookings', views.shop_bookings, name='shop-bookings'),
]