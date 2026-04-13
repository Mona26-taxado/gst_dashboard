"""
Portal access is restricted until the user signs the active agreement version.
"""

from django.conf import settings
from django.urls import Resolver404, resolve

AGREEMENT_REQUIRED_ROLES = frozenset(
    {
        "retailer",
        "distributor",
        "retailer_2",
        "distributor_2",
        "master_distributor",
    }
)


def user_has_signed_current_agreement(user):
    from dashboard.agreement_content import AGREEMENT_VERSION
    from dashboard.models import AgreementAcceptance

    return AgreementAcceptance.objects.filter(
        user=user, agreement_version=AGREEMENT_VERSION
    ).exists()


def pending_agreement_signing(user):
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_staff", False):
        return False
    role = getattr(user, "role", None)
    if role not in AGREEMENT_REQUIRED_ROLES:
        return False
    return not user_has_signed_current_agreement(user)


def path_exempt_from_agreement(request):
    path = request.path_info

    static_url = (getattr(settings, "STATIC_URL", None) or "/static/").rstrip("/") + "/"
    if path.startswith(static_url) or path.startswith("/static/"):
        return True

    media_url = getattr(settings, "MEDIA_URL", None) or ""
    if media_url:
        media_prefix = media_url if media_url.startswith("/") else f"/{media_url}"
        media_prefix = media_prefix.rstrip("/") + "/"
        if path.startswith(media_prefix):
            return True

    try:
        match = resolve(path)
    except Resolver404:
        return False

    return match.url_name in ("sign_agreement", "logout")
