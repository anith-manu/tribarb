from django.contrib import admin

# Register your models here.
from dashboard.models import Customer, Employee, Service, ServiceImage, Booking, BookingDetail

admin.site.register(Customer)
admin.site.register(Employee)
admin.site.register(Booking)
admin.site.register(BookingDetail)

class ServiceImageAdmin(admin.StackedInline):
    model = ServiceImage

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    inlines = [ServiceImageAdmin]

    class Meta:
        model = Service

@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    pass

