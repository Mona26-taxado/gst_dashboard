"""White-label tenant helpers. Platform users have tenant=NULL."""

from django.contrib.auth import get_user_model

from dashboard.models import WhiteLabelTenant

User = get_user_model()

WL_TREE_ROLES = frozenset(
    {
        "white_label_admin",
        "master_distributor",
        "distributor",
        "retailer",
    }
)

WL_CHILD_ROLES = frozenset(
    {
        "master_distributor",
        "distributor",
        "retailer",
    }
)


def normalize_host(host):
    if not host:
        return ""
    return host.split(":")[0].strip().lower()


def get_tenant_from_request(request):
    """Resolve WhiteLabelTenant from Host header, or None for platform/CSC."""
    host = normalize_host(request.get_host())
    if not host or host in ("localhost", "127.0.0.1", "testserver"):
        # Local: optional ?tenant=slug for testing
        slug = request.GET.get("tenant") or request.session.get("wl_tenant_slug")
        if slug:
            try:
                tenant = WhiteLabelTenant.objects.get(slug=slug, is_active=True)
                request.session["wl_tenant_slug"] = slug
                return tenant
            except WhiteLabelTenant.DoesNotExist:
                return None
        return None
    try:
        return WhiteLabelTenant.objects.get(domain__iexact=host, is_active=True)
    except WhiteLabelTenant.DoesNotExist:
        alt_host = host[4:] if host.startswith("www.") else f"www.{host}"
        try:
            return WhiteLabelTenant.objects.get(domain__iexact=alt_host, is_active=True)
        except WhiteLabelTenant.DoesNotExist:
            return None


def tenant_users_qs(tenant):
    if tenant is None:
        return User.objects.filter(tenant__isnull=True)
    return User.objects.filter(tenant=tenant)


def user_belongs_to_tenant(user, tenant):
    if not getattr(user, "is_authenticated", False):
        return False
    user_tenant_id = getattr(user, "tenant_id", None)
    if tenant is None:
        return user_tenant_id is None
    return user_tenant_id == tenant.id


def descendant_users(user, roles=None):
    """Users under this user in the referral tree, same tenant."""
    qs = User.objects.filter(tenant_id=user.tenant_id).exclude(pk=user.pk)
    if roles is not None:
        qs = qs.filter(role__in=list(roles))

    # BFS via referred_by chain rooted at user
    ids = set()
    frontier = list(User.objects.filter(referred_by=user).values_list("pk", flat=True))
    while frontier:
        ids.update(frontier)
        frontier = list(
            User.objects.filter(referred_by_id__in=frontier).values_list("pk", flat=True)
        )
        frontier = [i for i in frontier if i not in ids]

    return qs.filter(pk__in=ids)


def wl_admin_subtree_qs(wl_admin):
    """All users in the WL admin's tenant except other WL admins from other trees."""
    return User.objects.filter(tenant_id=wl_admin.tenant_id).exclude(
        role="white_label_admin"
    ).exclude(pk=wl_admin.pk)
