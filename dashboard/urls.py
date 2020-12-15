from django.urls import path
from . import views, apis
from django.contrib.auth.decorators import login_required

from django.conf.urls import url

urlpatterns = [
        path('', views.home, name='home'),
        path('shop/bookings', views.shop_bookings, name='shop-bookings'),
        path('shop/bookings/previous/', views.shop_bookings_completed, name='shop-bookings-completed'),
        path('shop/bookings/<int:booking_id>/', views.shop_view_booking, name='shop-view-booking'),

        path('shop/account', views.shop_account, name='shop-account'),

        path('shop/services', views.shop_services, name='shop-services'),
        path('shop/services/add/', views.shop_add_services, name='shop-add-services'),
        path('shop/services/edit/<int:service_id>/', views.shop_edit_services, name='shop-edit-services'),
        path('shop/services/album/<int:service_id>/', views.shop_service_album, name='shop-service-album'),

        path('shop/reports', views.shop_reports, name='shop-reports'),
        path('shop/employees', views.shop_employees, name='shop-employees'),
        url(r'^api/booking/notification/(?P<last_request_time>.+)/$', apis.shop_booking_notification),

        path('api/booking/get/<int:booking_id>/', apis.get_booking),

        #CUSTOMER API'S
        path('api/customer/stripe/', apis.stripe_ephemeral_key),
        path('api/customer/stripe/secret/', apis.get_stripe_client_secret),
        path('api/customer/shops/<int:filter_id>/', apis.customer_get_shops),
        path('api/customer/services/<int:filter_id>/<int:shop_id>/', apis.customer_get_services),
        path('api/customer/service/album/<int:service_id>/', apis.customer_get_service_album),
        path('api/customer/booking/add/', apis.customer_add_booking),
        path('api/customer/bookings/<int:filter_id>/', apis.customer_get_bookings),
        path('api/customer/shop/updaterating/', apis.customer_update_ratings),

        path('api/customer/booking/cancel/<int:booking_id>/', apis.customer_cancel_booking),
        path('api/customer/employee/location/', apis.customer_employee_location),

        path('api/customer/getinfo/', apis.customer_get_details),
        path('api/customer/updateinfo/', apis.customer_update_details),

        path('api/check/last-logged-in-as/', apis.check_user_last_loggin_in_as),
        path('api/set/last-logged-in-as/', apis.set_user_last_loggin_in_as),

        ##EMPLOYEE API'S
        path('api/employee/getinfo/', apis.employee_get_details),
        path('api/employee/updateinfo/', apis.employee_update_details),

        path('api/employee/verify/', apis.employee_verify),
        path('api/employee/bookings/<int:filter_id>/', apis.employee_get_bookings),
        path('api/employee/booking/accept/', apis.employee_accept_booking),
        path('api/employee/booking/decline/', apis.employee_decline_booking),
        path('api/employee/booking/enroute/', apis.employee_enroute),
        path('api/employee/booking/info/<int:booking_id>/', apis.employee_get_booking_info),
        path('api/employee/booking/complete/', apis.employee_complete_booking),
        path('api/employee/revenue/', apis.employee_get_revenue),
        path('api/employee/location/update/', apis.employee_update_location),

]