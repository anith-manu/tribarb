from django.urls import path
from . import views, apis
from django.contrib.auth.decorators import login_required

from django.conf.urls import url

urlpatterns = [
        path('', views.home, name='home'),
        path('bookings', views.shop_bookings, name='shop-bookings'),
        path('bookings/completed/', views.shop_bookings_completed, name='shop-bookings-completed'),

        path('account', views.shop_account, name='shop-account'),

        path('services', views.shop_services, name='shop-services'),
        path('services/add/', views.shop_add_services, name='shop-add-services'),
        path('services/edit/<int:service_id>/', views.shop_edit_services, name='shop-edit-services'),
        path('services/album/<int:service_id>/', views.shop_service_album, name='shop-service-album'),

        path('reports', views.shop_reports, name='shop-reports'),
        path('employees', views.shop_employees, name='shop-employees'),
        url(r'^api/booking/notification/(?P<last_request_time>.+)/$', apis.shop_booking_notification),

        #CUSTOMER API'S
        path('api/customer/shops/', apis.customer_get_shops),
        path('api/customer/services/<int:shop_id>/', apis.customer_get_services),
        path('api/customer/service/album/<int:service_id>/', apis.customer_get_service_album),
        path('api/customer/booking/add/', apis.customer_add_booking),
        path('api/customer/booking/latest/', apis.customer_get_latest_booking),
        #path('api/customer/employee/location/', apis.customer_employee_location),

]