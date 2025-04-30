from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordChangeView
from .views import not_authorized_view, custom_logout_view, CustomPasswordChangeView
from .views import admin_views, retailer_views, distributor_views, master_distributor_views
from .views import role_based_redirect
from .views.admin_views import update_pin  # Correct import for admin_views
from .views.admin_views import send_notifications, admin_view_transactions
from .views import pin_entry, account_settings  # Import the pin_entry view
from .views import additional_services, generate_qr_for_recharge  # Import the additional_services view
from .views.admin_views import add_gsk as admin_add_gsk, view_gsk as admin_view_gsk, add_or_deduct_money, edit_gsk, delete_gsk, service_billing, admin_view_transactions
from dashboard.views.admin_views import manage_notifications, delete_notification, delete_service_billing, manage_access_requests
from dashboard.views.admin_views import add_service, edit_service, delete_service # Import the necessary views
from dashboard.views import admin_views, retailer_views
from dashboard.views.retailer_views import add_customer as retailer_add_customer, delete_customer as retailer_delete_customer, retailer_view_transactions, wallet_recharge_view, banking_portal_request # Correct import statement
from dashboard.views import retailer_views
from dashboard.views.distributor_views import add_gsk, view_gsk, edit_gsk, delete_gsk, add_customer as distributor_add_customer, delete_customer, distributor_view_transactions, wallet_recharge_view, banking_portal_request
from .views.views import equipment_store, get_monthly_income_data
from .views.equipment_views import equipment_billing, equipment_payment, check_payment_status, payment_success, admin_equipment_billing, update_equipment_order_status
from .views import initiate_upi_payment


 #edit_customer  Import the function from retailer_views




urlpatterns = [
    
    path('redirect/', role_based_redirect, name='role_based_redirect'),
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    path('logout/', custom_logout_view, name='logout'),
    path('password-change/', PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),
    path('account/password-change/', CustomPasswordChangeView.as_view(
        template_name='account/password_change.html'
    ), name='password_change'),

    # Admin URLs
    path('not-authorized/', not_authorized_view, name='not_authorized'),
    path('qr-payment/<int:user_id>/', generate_qr_for_recharge, name='qr_payment'),

    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/add-gsk/', admin_add_gsk, name='admin_add_gsk'),
    path('admin/view-gsk/', admin_view_gsk, name='admin_view_gsk'),
    path('edit-gsk/<int:gsk_id>/', admin_views.edit_gsk, name='edit_gsk'),
    path('admin/delete-gsk/<int:user_id>/', admin_views.delete_gsk, name='delete_gsk'),
    # Admin URLs
    path('admin/view-billing/<int:billing_id>/', admin_views.view_billing_details, name='admin_view_billing_details'),
    path('delete-service/<int:service_id>/', delete_service, name='delete_service'),
    # Existing URL patterns
    path("admin/add-money/", add_or_deduct_money, name="add_or_deduct_money"),

    path("admin/view-transactions/", admin_view_transactions, name="view_transactions"),


     # Admin URLs
    path('admin/add-service/', add_service, name='add_service'),
    path('admin/view-services/', admin_views.view_services, name='view_services'),
    path('admin/edit-service/<int:service_id>/', edit_service, name='edit_service'),
    path('service-billing/', service_billing, name='service_billing'),
    path('delete-service-billing/<int:billing_id>/', delete_service_billing, name='delete_service_billing'),
    # Other URLs...
    path('notifications/manage/', manage_notifications, name='manage_notifications'),
    path('notifications/delete/<int:notification_id>/', delete_notification, name='delete_notification'),
    path('admin/manage-access-requests/', manage_access_requests, name='manage_access_requests'),

    

    path('dashboard/update-pin/<int:user_id>/', update_pin, name='update_pin'),



    # Retailer URLs
    path('retailer/dashboard/', retailer_views.retailer_dashboard, name='retailer_dashboard'),
    path('retailer/monthly-deductions/', retailer_views.get_retailer_monthly_deductions, name='retailer_monthly_deductions'),
    path('retailer/services-distribution/', retailer_views.get_services_distribution, name='retailer_services_distribution'),
    path('retailer/add-customer/', retailer_views.add_customer, name='retailer_add_customer'),
    path('retailer/view-customer/', retailer_views.view_customer, name='retailer_view_customer'),
    path('retailer/edit-customer/<int:customer_id>/', retailer_views.edit_customer, name='retailer_edit_customer'),
    path('retailer/delete-customer/<int:customer_id>/', retailer_views.delete_customer, name='retailer_delete_customer'),
    path('retailer/view-services/', retailer_views.view_services, name='retailer_view_services'),
    path('retailer/wallet-recharge/', wallet_recharge_view, name='wallet_recharge_page'),
    path('retailer/add-billing/', retailer_views.add_billing, name='retailer_add_billing'),
    path('banking-portal/request/', banking_portal_request, name='banking_portal_request'),
    
    path('retailer/view-billing/', retailer_views.view_billing, name='retailer_view_billing'),
    path('retailer/view-billing/<int:billing_id>/', retailer_views.view_billing_details, name='retailer_view_billing_details'),
    path('retailer/edit-billing/<int:billing_id>/', retailer_views.edit_billing, name='retailer_edit_billing'),
    path('dashboard/retailer/view-transactions/', retailer_view_transactions, name='retailer_view_transactions'),
    path('recharge-plans/', retailer_views.recharge_plans_view, name='recharge_plans'),



    # Distributor URLs
    path('distributor/dashboard/', distributor_views.distributor_dashboard, name='distributor_dashboard'),
    path('distributor/add-gsk/', distributor_views.add_gsk, name='distributor_add_gsk'),
    path('distributor/view-gsk/', distributor_views.view_gsk, name='distributor_view_gsk'),
    path('distributor/edit-gsk/<int:gsk_id>/', edit_gsk, name='distributor_edit_gsk'),
    path('distributor/add-customer/', distributor_views.add_customer, name='distributor_add_customer'),
    path('distributor/view-customer/', distributor_views.view_customer, name='distributor_view_customer'),
    path('distributor/edit-customer/<int:customer_id>/', distributor_views.edit_customer, name='distributor_edit_customer'),
    path('distributor/delete-customer/<int:customer_id>/', distributor_views.delete_customer, name='distributor_delete_customer'),
    path('distributor/view-services/', distributor_views.view_services, name='distributor_view_services'),
    path('distributor/wallet-recharge/', wallet_recharge_view, name='wallet_recharge_page'),
    path('distributor/add-billing/', distributor_views.add_billing, name='distributor_add_billing'),
    path('banking-portal/request/', banking_portal_request, name='banking_portal_request'),
    
    path('distributor/view-billing/', distributor_views.view_billing, name='distributor_view_billing'),
    path('distributor/edit-billing/<int:billing_id>/', distributor_views.edit_billing, name='distributor_edit_billing'),
    path('distributor/delete-gsk/<int:gsk_id>/', distributor_views.delete_gsk, name='distributor_delete_gsk'),
    path('distributor/view-billing/<int:billing_id>/', distributor_views.view_billing_details, name='distributor_view_billing_details'),
    path('dashboard/distributor/view-transactions/', distributor_view_transactions, name='distributor_view_transactions'),
    path('distributor/transfer-money/', distributor_views.transfer_money, name='transfer_money'),



    # Master Distributor URLs
    path('master-distributor/dashboard/', master_distributor_views.master_distributor_dashboard, name='master_distributor_dashboard'),

    # Other routes
    path('pin-entry/', pin_entry, name='pin_entry'),
    # Other routes
    path('send-notifications/', send_notifications, name='send_notifications'),
    # Other routes
    path('additional-services/', additional_services, name='additional_services'),
    path('account/settings/', account_settings, name='account_settings'),
    path('equipment-store/', equipment_store, name='equipment_store'),
    path('equipment-store/billing/<int:equipment_id>/', equipment_billing, name='equipment_billing'),
    path('equipment-store/payment/', equipment_payment, name='equipment_payment'),
    path('equipment-store/check-payment-status/<int:order_id>/', check_payment_status, name='check_payment_status'),
    path('equipment-store/payment/success/<int:order_id>/', payment_success, name='payment_success'),
    path('equipment-store/admin-billing/', admin_equipment_billing, name='admin_equipment_billing'),
    path('equipment-store/update-order-status/<int:order_id>/', update_equipment_order_status, name='update_equipment_order_status'),
    path('get-monthly-income-data/', get_monthly_income_data, name='get_monthly_income_data'),
    path('initiate-upi-payment/', initiate_upi_payment, name='initiate_upi_payment'),

]
