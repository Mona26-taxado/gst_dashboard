from django.contrib import admin
from .models import (
    CustomUser, CSCService, CSCServiceRequest, CSCServiceDocument,
    BillingDetails, Customer, Retailer2BillingDetails
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email')


@admin.register(CSCService)
class CSCServiceAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'price', 'wallet_deduction', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('service_name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CSCServiceRequest)
class CSCServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('retailer', 'service', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('retailer__username', 'service__service_name')
    readonly_fields = ('created_at',)


@admin.register(CSCServiceDocument)
class CSCServiceDocumentAdmin(admin.ModelAdmin):
    list_display = ('service', 'document_name', 'is_required')
    list_filter = ('is_required',)
    search_fields = ('service__service_name', 'document_name')


@admin.register(BillingDetails)
class BillingDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'service', 'amount', 'payment_status', 'billing_date')
    list_filter = ('payment_status', 'billing_date')
    search_fields = ('customer__full_name', 'service__service_name')
    readonly_fields = ('billing_date',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'mobile', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('full_name', 'mobile', 'created_by__username')
    readonly_fields = ('created_at',)


@admin.register(Retailer2BillingDetails)
class Retailer2BillingDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'service', 'amount', 'payment_status', 'billing_date')
    list_filter = ('payment_status', 'billing_date')
    search_fields = ('customer__full_name', 'service__service_name')
    readonly_fields = ('billing_date',)


