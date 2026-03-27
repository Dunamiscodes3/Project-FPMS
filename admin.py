from django.contrib import admin
from .models import (User, Farmer, Credit, Delivery,
                     MachineryBooking, Payment, SeedDistribution, SoilHealthLog)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'full_name', 'role', 'created_at']
    list_filter  = ['role']

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ['farmer_id', 'full_name', 'phone', 'location', 'farm_size', 'status']
    list_filter  = ['status']
    search_fields = ['full_name', 'id_number', 'phone']

@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ['credit_id', 'farmer', 'credit_type', 'amount', 'outstanding', 'status']
    list_filter  = ['status', 'credit_type']

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['delivery_id', 'farmer', 'delivery_date', 'weight', 'variety', 'milling_status']
    list_filter  = ['milling_status', 'variety']

@admin.register(MachineryBooking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'farmer', 'machinery_type', 'requested_date', 'status']
    list_filter  = ['status', 'machinery_type']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'farmer', 'amount', 'method', 'date_paid']

@admin.register(SeedDistribution)
class SeedAdmin(admin.ModelAdmin):
    list_display = ['seed_id', 'farmer', 'variety', 'quantity_kg', 'supplier_quality']

@admin.register(SoilHealthLog)
class SoilAdmin(admin.ModelAdmin):
    list_display = ['log_id', 'farmer', 'ph_level', 'moisture_level', 'water_status', 'log_date']
