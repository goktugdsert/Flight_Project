from django.contrib import admin
from .models import Flight, Passenger, Airport, VehicleType

admin.site.register(Flight)
admin.site.register(Passenger)
admin.site.register(Airport)
admin.site.register(VehicleType)