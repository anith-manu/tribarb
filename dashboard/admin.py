from django.contrib import admin

# Register your models here.
from dashboard.models import Customer, Employee, Service, ServiceImage

admin.site.register(Customer)
admin.site.register(Employee)
#admin.site.register(Service)
#admin.site.register(ServiceImage)

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

