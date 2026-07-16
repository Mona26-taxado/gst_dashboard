from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponseForbidden
from django.contrib import messages

from dashboard.agreement_gate import path_exempt_from_agreement, pending_agreement_signing
from dashboard.tenant import get_tenant_from_request, normalize_host




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
    Domain-based access:
    - White Label tenant domain → request.tenant set; only that tenant's users
    - CRM domain: Admin, Distributor, Retailer (v1), platform users (tenant=NULL)
    - CSC domain: Retailer 2.0 / Distributor 2.0
    Existing CRM/CSC behaviour preserved; WL is an additive branch.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_domain = request.get_host()
        host_only = normalize_host(current_domain)

        crm_domains = getattr(settings, 'CRM_ALLOWED_DOMAINS', [])
        csc_domains = getattr(settings, 'CSC_ALLOWED_DOMAINS', [])

        is_local_development = self._is_local_development(current_domain)
        tenant = get_tenant_from_request(request)
        request.tenant = tenant

        is_crm_domain = self._check_domain_access(current_domain, crm_domains)
        is_csc_domain = self._check_domain_access(current_domain, csc_domains)

        # White-label host takes precedence over CRM/CSC lists
        if tenant is not None:
            request.domain_type = 'white_label'
            if request.user.is_authenticated:
                user_role = getattr(request.user, 'role', None)
                if user_role == 'admin':
                    # Super Admin stays on CRM — bounce off WL domains
                    return redirect(f"https://{settings.CRM_DOMAIN}/")
                if getattr(request.user, 'tenant_id', None) != tenant.id:
                    from django.contrib.auth import logout
                    logout(request)
                    messages.error(request, "Access denied for this portal.")
                    return redirect('login')
            return self.get_response(request)

        if not (is_crm_domain or is_csc_domain) and not is_local_development:
            return HttpResponseForbidden("Access denied. Invalid domain.")

        if is_local_development:
            request.domain_type = 'local'
        else:
            request.domain_type = 'crm' if is_crm_domain else 'csc'

        # Authenticated users — production cross-domain redirects (unchanged for CRM/CSC)
        if request.user.is_authenticated and not is_local_development:
            user_role = request.user.role

            # White Label admins must use their tenant domain, not CRM
            if user_role == 'white_label_admin' and is_crm_domain:
                tenant_obj = getattr(request.user, 'tenant', None)
                if tenant_obj and tenant_obj.domain:
                    return redirect(f"https://{tenant_obj.domain}/")
                return HttpResponseForbidden("White Label portal domain is not configured.")

            if is_csc_domain:
                if user_role not in ['retailer_2', 'distributor_2']:
                    return redirect(f"https://{settings.CRM_DOMAIN}{request.path}")

            elif is_crm_domain:
                if user_role in ['retailer_2', 'distributor_2']:
                    return redirect(f"https://{settings.CSC_DOMAIN}{request.path}")
                # Platform CRM: reject users that belong to a WL tenant
                if getattr(request.user, 'tenant_id', None) is not None and user_role != 'admin':
                    tenant_obj = getattr(request.user, 'tenant', None)
                    if tenant_obj and tenant_obj.domain:
                        return redirect(f"https://{tenant_obj.domain}/")

        response = self.get_response(request)
        return response

    def _check_domain_access(self, current_domain, allowed_domains):
        """Check if current domain is in allowed domains list"""
        if current_domain in allowed_domains:
            return True

        domain_without_port = current_domain.split(':')[0]
        if domain_without_port in allowed_domains:
            return True

        for port in ['8000', '80', '443']:
            domain_with_port = f"{domain_without_port}:{port}"
            if domain_with_port in allowed_domains:
                return True

        return False

    def _is_local_development(self, current_domain):
        """Check if current domain is for local development"""
        local_domains = [
            'localhost', '127.0.0.1', 'localhost:8000', '127.0.0.1:8000',
            'testserver',  # Django test client
        ]

        if current_domain in local_domains:
            return True

        domain_without_port = current_domain.split(':')[0]
        if domain_without_port in ['localhost', '127.0.0.1', 'testserver']:
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
        response = self.get_response(request)
        return response


class AgreementRequiredMiddleware:
    """
    Block portal URLs until the user has signed the active agreement version.
    Only sign_agreement and logout (plus static/media) are allowed while pending.
    """

    _NOTICE = (
        "Agreement required: You cannot use the rest of the portal until you read and sign "
        "the Terms & Conditions on this page."
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.agreement_pending = False

        if not request.user.is_authenticated:
            return self.get_response(request)

        if pending_agreement_signing(request.user):
            request.agreement_pending = True
            if not path_exempt_from_agreement(request):
                if not request.session.get("agreement_block_notice_shown"):
                    messages.warning(request, self._NOTICE)
                    request.session["agreement_block_notice_shown"] = True
                return redirect("sign_agreement")

        return self.get_response(request)
