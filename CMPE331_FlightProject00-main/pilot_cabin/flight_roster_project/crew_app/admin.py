from django.contrib import admin
from .models import Pilot, CabinAttendant, VehicleType, Language, DishRecipe

@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'total_seats', 'business_seats', 'economy_seats']
    search_fields = ['code', 'name']

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']

@admin.register(Pilot)
class PilotAdmin(admin.ModelAdmin):
    list_display = ['pilot_id', 'full_name', 'age', 'seniority_level', 'vehicle_type', 'is_active']
    list_filter = ['seniority_level', 'vehicle_type', 'is_active']
    search_fields = ['first_name', 'last_name', 'license_number']
    filter_horizontal = ['known_languages']

@admin.register(CabinAttendant)
class CabinAttendantAdmin(admin.ModelAdmin):
    list_display = ['attendant_id', 'full_name', 'age', 'attendant_type', 'is_active']
    list_filter = ['attendant_type', 'is_active']
    search_fields = ['first_name', 'last_name', 'employee_number']
    filter_horizontal = ['known_languages', 'allowed_vehicle_types']

@admin.register(DishRecipe)
class DishRecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'chef', 'cuisine_type', 'preparation_time', 'is_active']
    list_filter = ['cuisine_type', 'is_active']
    search_fields = ['name', 'chef__first_name', 'chef__last_name']