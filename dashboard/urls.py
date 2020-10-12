from django.urls import path
from . import views, apis
from django.contrib.auth.decorators import login_required

urlpatterns = [
        path('', views.home, name='home'),
        path('bookings', views.shop_bookings, name='shop-bookings'),
        path('account', views.shop_account, name='shop-account'),

        path('services', views.shop_services, name='shop-services'),
        path('services/add/', views.shop_add_services, name='shop-add-services'),
        path('services/edit/<int:service_id>/', views.shop_edit_services, name='shop-edit-services'),
        path('services/album/<int:service_id>/', views.shop_service_album, name='shop-service-album'),

        path('reports', views.shop_reports, name='shop-reports'),
        path('employees', views.shop_employees, name='shop-employees'),


        path('api/customer/shops/', apis.customer_get_shops),

]