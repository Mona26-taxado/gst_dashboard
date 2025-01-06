from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordChangeView
from .views import not_authorized_view, custom_logout_view, CustomPasswordChangeView
from .views import admin_views, retailer_views, distributor_views, master_distributor_views
from .views import role_based_redirect
from .views.admin_views import update_pin  # Correct import for admin_views
from .views.admin_views import send_notifications, admin_view_transactions
from .views import pin_entry, account_settings  # Import the pin_entry view
from .views import additional_services  # Import the additional_services view
from .views.admin_views import add_gsk, view_gsk, add_or_deduct_money, edit_gsk, delete_gsk, service_billing, admin_view_transactions
from dashboard.views.admin_views import manage_notifications, delete_notification, delete_service_billing
from dashboard.views.admin_views import add_service, edit_service, delete_service # Import the necessary views
from dashboard.views import admin_views, retailer_views
from dashboard.views.retailer_views import delete_customer, retailer_view_transactions, generate_qr_for_recharge, wallet_recharge_view # Correct import statement
from dashboard.views import retailer_views


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
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('add-gsk/', add_gsk, name='add_gsk'),
    path('view-gsk/', view_gsk, name='view_gsk'),
    path('dashboard/admin/edit-gsk/<int:user_id>/', admin_views.edit_gsk, name='edit_gsk'),
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

    path('dashboard/update-pin/<int:user_id>/', update_pin, name='update_pin'),



    # Retailer URLs
    path('retailer/dashboard/', retailer_views.retailer_dashboard, name='retailer_dashboard'),
    path('add_customer/', retailer_views.add_customer, name='add_customer'),
    path('view_customer/', retailer_views.view_customer, name='view_customer'),
    path('edit_customer/<int:customer_id>/', retailer_views.edit_customer, name='edit_customer'),  # Ensure this name matches
    path('retailer/delete-customer/<int:customer_id>/', retailer_views.delete_customer, name='retailer_delete_customer'),
    path('retailer/view-services/', retailer_views.view_services, name='retailer_view_services'),
    path('retailer/qr-payment/<int:user_id>/', generate_qr_for_recharge, name='qr_payment'),
    path('retailer/wallet-recharge/', wallet_recharge_view, name='wallet_recharge_page'),
    path('add-billing/', retailer_views.add_billing, name='add_billing'),
    
    path('view-billing/', retailer_views.view_billing, name='view_billing'),
    path('view-billing/<int:billing_id>/', retailer_views.view_billing_details, name='view_billing_details'),
    path('edit-billing/<int:billing_id>/', retailer_views.edit_billing, name='edit_billing'),
    path('dashboard/retailer/view-transactions/', retailer_view_transactions, name='retailer_view_transactions'),


    # Distributor URLs
    path('distributor/dashboard/', distributor_views.distributor_dashboard, name='distributor_dashboard'),

    # Master Distributor URLs
    path('master-distributor/dashboard/', master_distributor_views.master_distributor_dashboard, name='master_distributor_dashboard'),

    # Other routes
    path('pin-entry/', pin_entry, name='pin_entry'),
    # Other routes
    path('send-notifications/', send_notifications, name='send_notifications'),
    # Other routes
    path('additional-services/', additional_services, name='additional_services'),
    path('account/settings/', account_settings, name='account_settings'),

]
