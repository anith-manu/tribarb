from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', login_required(views.BookingsView.as_view()), name='bookings'),
    path('bookings', login_required(views.BookingsView.as_view()), name='bookings'),
]