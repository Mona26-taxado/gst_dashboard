from datetime import datetime

from dashboard.models import Wallet
from dashboard.tenant import WL_TREE_ROLES, wl_admin_subtree_qs
from dashboard.utils import is_wl_tenant_user

TENANT_DASHBOARD_URLS = {
    "white_label_admin": "/wl/dashboard/",
    "retailer": "/retailer/dashboard/",
    "distributor": "/distributor/dashboard/",
    "master_distributor": "/master-distributor/dashboard/",
}


def tenant_branding(request):
    tenant = getattr(request, "tenant", None)
    user = getattr(request, "user", None)
    ctx = {
        "tenant": tenant,
        "wl_wallet_balance": 0,
        "total_centers": 0,
        "uses_wl_theme": False,
        "tenant_dashboard_url": "/",
    }
    if user is not None and getattr(user, "is_authenticated", False):
        role = getattr(user, "role", None)
        if is_wl_tenant_user(user):
            ctx["uses_wl_theme"] = True
            tenant = getattr(user, "tenant", None) or tenant
            ctx["tenant"] = tenant
            ctx["tenant_dashboard_url"] = TENANT_DASHBOARD_URLS.get(role, "/")
            if role == "white_label_admin":
                ctx["total_centers"] = wl_admin_subtree_qs(user).count()
            wallet, _ = Wallet.objects.get_or_create(user=user)
            ctx["wl_wallet_balance"] = wallet.balance
            hour = datetime.now().hour
            if hour < 12:
                ctx["greeting"] = "Good morning"
            elif hour < 17:
                ctx["greeting"] = "Good afternoon"
            else:
                ctx["greeting"] = "Good evening"
        elif role in WL_TREE_ROLES and getattr(user, "tenant_id", None):
            tenant = getattr(user, "tenant", None) or tenant
            ctx["tenant"] = tenant
    return ctx
