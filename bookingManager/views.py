from django.shortcuts import redirect, render
from django.views.generic import View

# Create your views here.
class BookingsView(View):
    def get(self, request):
        return render(request, 'dashboard/bookings.html')
