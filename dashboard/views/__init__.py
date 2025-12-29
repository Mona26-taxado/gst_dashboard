# Import views to expose them for dashboard.views
from .views import not_authorized_view
from .admin_views import admin_dashboard
from .retailer_views import retailer_dashboard
from .distributor_views import distributor_dashboard
from .views import role_based_redirect, admin_redirect_view  # Add this line to expose the function
from .views import pin_entry
from .views import additional_services, generate_qr_for_recharge  # Import the additional_services view
from .admin_views import add_service, view_services
from .views import custom_logout_view
from .views import account_settings, CustomPasswordChangeView
from .payment_views import initiate_upi_payment

__all__ = ['add_service', 'view_services', 'initiate_upi_payment']

# This file is intentionally empty to make the directory a Python package

# This file makes the views directory a Python package

