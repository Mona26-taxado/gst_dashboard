from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseForbidden




def role_required(roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You do not have permission to access this page.")
        return _wrapped_view
    return decorator






#To ensure extra security across all views, you can add middleware that checks the role before allowing access to the update_pin view.
class DomainAccessMiddleware:
    """
    Middleware to handle domain-based access control for multi-domain setup.
    - CRM domain (crm.grahaksahaayatakendra.com): Admin, Distributor, Retailer (v1)
    - CSC domain (clasclass.com): Retailer 2.0 only
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get current domain
        current_domain = request.get_host()
        
        # Get allowed domains from settings
        crm_domains = getattr(settings, 'CRM_ALLOWED_DOMAINS', [])
        csc_domains = getattr(settings, 'CSC_ALLOWED_DOMAINS', [])
        
        # Check if current domain is valid
        is_crm_domain = self._check_domain_access(current_domain, crm_domains)
        is_csc_domain = self._check_domain_access(current_domain, csc_domains)
        
        # For local development, allow all domains without redirects
        is_local_development = self._is_local_development(current_domain)
        
        if not (is_crm_domain or is_csc_domain) and not is_local_development:
            return HttpResponseForbidden("Access denied. Invalid domain.")
        
        # Store domain type in request for use in views
        if is_local_development:
            request.domain_type = 'local'
        else:
            request.domain_type = 'crm' if is_crm_domain else 'csc'
        
        # Handle authenticated users - only redirect in production
        if request.user.is_authenticated and not is_local_development:
            user_role = request.user.role
            
            # CSC domain restrictions
            if is_csc_domain:
                if user_role not in ['retailer_2', 'distributor_2']:
                    # Redirect non-CSC users to CRM domain
                    return redirect(f"https://{settings.CRM_DOMAIN}{request.path}")
            
            # CRM domain restrictions
            elif is_crm_domain:
                if user_role in ['retailer_2', 'distributor_2']:
                    # Redirect CSC users to CSC domain
                    return redirect(f"https://{settings.CSC_DOMAIN}{request.path}")
        
        response = self.get_response(request)
        return response
    
    def _check_domain_access(self, current_domain, allowed_domains):
        """Check if current domain is in allowed domains list"""
        # Check exact match first
        if current_domain in allowed_domains:
            return True
        
        # Check without port number
        domain_without_port = current_domain.split(':')[0]
        if domain_without_port in allowed_domains:
            return True
        
        # Check with common ports
        for port in ['8000', '80', '443']:
            domain_with_port = f"{domain_without_port}:{port}"
            if domain_with_port in allowed_domains:
                return True
        
        return False
    
    def _is_local_development(self, current_domain):
        """Check if current domain is for local development"""
        local_domains = ['localhost', '127.0.0.1', 'localhost:8000', '127.0.0.1:8000']
        
        # Check exact match
        if current_domain in local_domains:
            return True
        
        # Check without port
        domain_without_port = current_domain.split(':')[0]
        if domain_without_port in ['localhost', '127.0.0.1']:
            return True
        
        return False


class AdminOnlyMiddleware:
    """
    Existing middleware for admin-only access control.
    Kept for backward compatibility.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Your existing admin middleware logic here
        response = self.get_response(request)
        return response
