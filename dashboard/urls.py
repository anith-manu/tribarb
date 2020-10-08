from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
        path('', views.home, name='home'),
        path('bookings', views.shop_bookings, name='shop-bookings'),
        path('account', views.shop_account, name='shop-account'),
        path('services', views.shop_services, name='shop-services'),
        path('reports', views.shop_reports, name='shop-reports'),
        path('employees', views.shop_employees, name='shop-employees'),

]