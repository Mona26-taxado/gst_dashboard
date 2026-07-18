"""White Label Admin dashboard — reuses GSK patterns with tenant scoping."""

import json
from decimal import Decimal
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from dashboard.forms import AddGSKForm
from dashboard.models import (
    BankingPortalAccessRequest,
    BillingDetails,
    CustomUser,
    Service,
    Transaction,
    Wallet,
)
from dashboard.tenant import WL_CHILD_ROLES, wl_admin_subtree_qs
from dashboard.utils import role_required
from dashboard.wallet_ops import WalletError, transfer_wallet


def _require_tenant(user):
    return bool(user.tenant_id)


def _wl_context(request, **extra):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    ctx = {
        "wallet_balance": wallet.balance,
        "tenant": request.user.tenant or getattr(request, "tenant", None),
    }
    ctx.update(extra)
    return ctx


def _tenant_user_ids(user):
    return list(
        CustomUser.objects.filter(tenant_id=user.tenant_id).values_list("id", flat=True)
    )


@login_required
@role_required(["white_label_admin"])
def white_label_dashboard(request):
    if not _require_tenant(request.user):
        messages.error(request, "No tenant linked to your account.")
        return redirect("logout")

    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    subtree = wl_admin_subtree_qs(request.user)
    tenant_ids = _tenant_user_ids(request.user)

    recent_users = subtree.order_by("-created_at")[:6]
    recent_txns = (
        Transaction.objects.filter(user_id__in=tenant_ids)
        .select_related("user")
        .order_by("-created_at")[:8]
    )
    recent_billings = (
        BillingDetails.objects.filter(user_id__in=tenant_ids)
        .select_related("customer", "service", "user")
        .order_by("-billing_date")[:6]
    )

    month = timezone.now().month
    year = timezone.now().year
    monthly_billing = (
        BillingDetails.objects.filter(
            user_id__in=tenant_ids,
            billing_date__month=month,
            billing_date__year=year,
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    total_billing = (
        BillingDetails.objects.filter(user_id__in=tenant_ids).aggregate(
            total=Sum("amount"), count=Count("id")
        )
    )
    txn_count = Transaction.objects.filter(user_id__in=tenant_ids).count()

    total_md = subtree.filter(role="master_distributor").count()
    total_distributors = subtree.filter(role="distributor").count()
    total_retailers = subtree.filter(role="retailer").count()

    role_chart = [
        {"label": "Master Distributors", "value": total_md, "color": "#0e7490"},
        {"label": "Distributors", "value": total_distributors, "color": "#2563eb"},
        {"label": "Retailers", "value": total_retailers, "color": "#16a34a"},
    ]
    max_role = max((r["value"] for r in role_chart), default=1) or 1
    for item in role_chart:
        item["pct"] = round((item["value"] / max_role) * 100)

    monthly_trend = []
    for i in range(5, -1, -1):
        dt = timezone.now() - timedelta(days=i * 30)
        amt = (
            BillingDetails.objects.filter(
                user_id__in=tenant_ids,
                billing_date__month=dt.month,
                billing_date__year=dt.year,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        monthly_trend.append({"label": dt.strftime("%b"), "amount": float(amt)})

    hour = timezone.localtime().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    context = _wl_context(
        request,
        total_centers=subtree.count(),
        total_users=subtree.count(),
        total_md=total_md,
        total_distributors=total_distributors,
        total_retailers=total_retailers,
        total_services=Service.objects.filter(status="active").count(),
        total_customer_billing=total_billing["total"] or 0,
        total_customer_billing_count=total_billing["count"] or 0,
        monthly_billing=monthly_billing,
        txn_count=txn_count,
        role_chart=role_chart,
        monthly_trend_json=json.dumps(monthly_trend),
        greeting=greeting,
        recent_users=recent_users,
        recent_txns=recent_txns,
        recent_billings=recent_billings,
        wallet_balance=wallet.balance,
    )
    return render(request, "white_label_dashboard/dashboard.html", context)


@login_required
@role_required(["white_label_admin"])
def white_label_add_user(request):
    if not _require_tenant(request.user):
        return redirect("logout")

    allowed = list(WL_CHILD_ROLES)
    parents = CustomUser.objects.filter(
        tenant_id=request.user.tenant_id,
        role__in=["white_label_admin", "master_distributor", "distributor"],
        is_active=True,
    ).order_by("full_name")

    if request.method == "POST":
        form = AddGSKForm(request.POST, allowed_roles=allowed)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.tenant = request.user.tenant
                referred_by_id = request.POST.get("referred_by")
                if referred_by_id:
                    parent = get_object_or_404(
                        CustomUser,
                        id=referred_by_id,
                        tenant_id=request.user.tenant_id,
                    )
                    user.referred_by = parent
                else:
                    user.referred_by = request.user
                user.save()
                messages.success(request, f"User {user.full_name} created.")
                return redirect("white_label_view_users")
            except IntegrityError:
                messages.error(
                    request,
                    "Could not create user. Email or Branch ID already exists.",
                )
            except Exception as exc:
                messages.error(request, f"An error occurred: {exc}")
        else:
            messages.error(request, "Please fix the errors highlighted below.")
    else:
        form = AddGSKForm(
            allowed_roles=allowed,
            initial={"start_date": timezone.now().date()},
        )

    return render(
        request,
        "white_label_dashboard/add_user.html",
        _wl_context(request, form=form, parents=parents),
    )


@login_required
@role_required(["white_label_admin"])
def white_label_view_users(request):
    if not _require_tenant(request.user):
        return redirect("logout")

    search_query = request.GET.get("search", "")
    role_filter = request.GET.get("role", "")
    users = wl_admin_subtree_qs(request.user).order_by("-created_at")
    if search_query:
        users = users.filter(
            Q(full_name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(branch_id__icontains=search_query)
        )
    if role_filter in WL_CHILD_ROLES:
        users = users.filter(role=role_filter)

    paginator = Paginator(users, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "white_label_dashboard/view_users.html",
        _wl_context(
            request,
            page_obj=page_obj,
            search_query=search_query,
            role_filter=role_filter,
            serial_start=(page_obj.number - 1) * paginator.per_page,
        ),
    )


@login_required
@role_required(["white_label_admin"])
def white_label_edit_user(request, user_id):
    if not _require_tenant(request.user):
        return redirect("logout")

    user = get_object_or_404(
        CustomUser,
        id=user_id,
        tenant_id=request.user.tenant_id,
    )
    if user.role == "white_label_admin":
        messages.error(request, "Cannot edit another White Label Admin here.")
        return redirect("white_label_view_users")

    allowed = list(WL_CHILD_ROLES)
    parents = CustomUser.objects.filter(
        tenant_id=request.user.tenant_id,
        role__in=["white_label_admin", "master_distributor", "distributor"],
        is_active=True,
    ).exclude(pk=user.pk).order_by("full_name")

    if request.method == "POST":
        form = AddGSKForm(request.POST, instance=user, allowed_roles=allowed)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.tenant = request.user.tenant
            referred_by_id = request.POST.get("referred_by")
            if referred_by_id:
                updated.referred_by = get_object_or_404(
                    CustomUser, id=referred_by_id, tenant_id=request.user.tenant_id
                )
            updated.save()
            messages.success(request, "User updated.")
            return redirect("white_label_view_users")
    else:
        form = AddGSKForm(instance=user, allowed_roles=allowed)

    return render(
        request,
        "white_label_dashboard/edit_user.html",
        _wl_context(request, form=form, gsk=user, parents=parents),
    )


@login_required
@role_required(["white_label_admin"])
def white_label_delete_user(request, user_id):
    if not _require_tenant(request.user):
        return redirect("logout")

    user = get_object_or_404(
        CustomUser,
        id=user_id,
        tenant_id=request.user.tenant_id,
    )
    if user.role == "white_label_admin" or user.pk == request.user.pk:
        messages.error(request, "Cannot delete this user.")
        return redirect("white_label_view_users")

    if request.method == "POST":
        name = user.full_name
        user.delete()
        messages.success(request, f"Deleted {name}.")
        return redirect("white_label_view_users")

    return render(
        request,
        "white_label_dashboard/delete_user.html",
        _wl_context(request, gsk=user),
    )


@login_required
@role_required(["white_label_admin"])
def white_label_add_wallet(request):
    if not _require_tenant(request.user):
        return redirect("logout")

    import base64
    from io import BytesIO

    from PIL import Image as PILImage

    from dashboard.models import QRCodeSettings
    from dashboard.utils import generate_qr

    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    user_name = request.user.full_name

    qr_settings = QRCodeSettings.objects.first()
    if qr_settings and qr_settings.qr_code_image:
        qr_image = PILImage.open(qr_settings.qr_code_image)
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        qr_code_b64 = base64.b64encode(buffer.getvalue()).decode()
        qr_code_src = f"data:image/png;base64,{qr_code_b64}"
    else:
        qr_code_path = generate_qr(user_name)
        qr_code_src = f"/static/{qr_code_path}"

    show_wallet_disclaimer = not request.session.get("wallet_disclaimer_dismissed", False)

    return render(
        request,
        "white_label_dashboard/add_wallet.html",
        _wl_context(
            request,
            user_name=user_name,
            qr_code_src=qr_code_src,
            show_wallet_disclaimer=show_wallet_disclaimer,
        ),
    )


@login_required
@role_required(["white_label_admin"])
def white_label_transfer_money(request):
    if not _require_tenant(request.user):
        return redirect("logout")

    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    recipients = wl_admin_subtree_qs(request.user).filter(
        role__in=list(WL_CHILD_ROLES),
        is_active=True,
    ).order_by("full_name")

    if request.method == "POST":
        recipient_id = request.POST.get("recipient_id")
        try:
            amount = Decimal(request.POST.get("amount") or "0")
        except Exception:
            messages.error(request, "Invalid amount.")
            return redirect("white_label_transfer_money")

        try:
            recipient = recipients.get(id=recipient_id)
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid recipient.")
            return redirect("white_label_transfer_money")

        try:
            transfer_wallet(
                request.user,
                recipient,
                amount,
                debit_description=f"WL transfer to {recipient.full_name} ({recipient.role})",
                credit_description=f"Received from WL Admin: {request.user.full_name}",
            )
            messages.success(
                request,
                f"Transferred ₹{amount} to {recipient.full_name}.",
            )
        except WalletError as e:
            messages.error(request, str(e))
        return redirect("white_label_transfer_money")

    return render(
        request,
        "white_label_dashboard/transfer_money.html",
        _wl_context(request, recipients=recipients, wallet_balance=wallet.balance),
    )


@login_required
@role_required(["white_label_admin"])
def white_label_view_transactions(request):
    if not _require_tenant(request.user):
        return redirect("logout")

    tenant_user_ids = _tenant_user_ids(request.user)
    transactions = (
        Transaction.objects.filter(user_id__in=tenant_user_ids)
        .select_related("user")
        .order_by("-created_at")
    )
    search_query = request.GET.get("search", "")
    if search_query:
        transactions = transactions.filter(
            Q(user__full_name__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    paginator = Paginator(transactions, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "white_label_dashboard/view_transactions.html",
        _wl_context(request, page_obj=page_obj, search_query=search_query),
    )


@login_required
@role_required(["white_label_admin"])
def white_label_view_services(request):
    if not _require_tenant(request.user):
        return redirect("logout")

    search_query = request.GET.get("search", "")
    services = Service.objects.filter(status="active").order_by("service_name")
    if search_query:
        services = services.filter(service_name__icontains=search_query)

    paginator = Paginator(services, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "white_label_dashboard/view_services.html",
        _wl_context(
            request,
            page_obj=page_obj,
            search_query=search_query,
            serial_start=(page_obj.number - 1) * paginator.per_page,
        ),
    )


@login_required
@role_required(["white_label_admin"])
def white_label_service_documents(request, service_id):
    if not _require_tenant(request.user):
        return redirect("logout")

    service = get_object_or_404(Service, pk=service_id, status="active")
    return render(
        request,
        "white_label_dashboard/service_documents.html",
        _wl_context(
            request,
            service=service,
            document_items=service.required_documents_list(),
        ),
    )


@login_required
@role_required(["white_label_admin"])
def white_label_view_billing(request):
    if not _require_tenant(request.user):
        return redirect("logout")

    tenant_ids = _tenant_user_ids(request.user)
    search_query = request.GET.get("search", "")
    billings = (
        BillingDetails.objects.filter(user_id__in=tenant_ids)
        .select_related("customer", "service", "user")
        .order_by("-billing_date")
    )
    if search_query:
        billings = billings.filter(
            Q(ref_no__icontains=search_query)
            | Q(customer__full_name__icontains=search_query)
            | Q(user__full_name__icontains=search_query)
            | Q(service__service_name__icontains=search_query)
        )

    paginator = Paginator(billings, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "white_label_dashboard/view_billing.html",
        _wl_context(request, page_obj=page_obj, search_query=search_query),
    )


@login_required
@role_required(["white_label_admin"])
def white_label_reports(request):
    if not _require_tenant(request.user):
        return redirect("logout")

    subtree = wl_admin_subtree_qs(request.user)
    tenant_ids = _tenant_user_ids(request.user)

    role_breakdown = (
        subtree.values("role")
        .annotate(total=Count("id"))
        .order_by("role")
    )

    billing_qs = BillingDetails.objects.filter(user_id__in=tenant_ids)
    billing_summary = billing_qs.aggregate(
        total_amount=Sum("amount"),
        total_count=Count("id"),
    )
    paid_count = billing_qs.filter(payment_status="Paid").count()
    unpaid_count = billing_qs.filter(payment_status="Unpaid").count()

    txn_qs = Transaction.objects.filter(user_id__in=tenant_ids)
    credit_total = (
        txn_qs.filter(transaction_type="Credit").aggregate(t=Sum("amount"))["t"] or 0
    )
    debit_total = (
        txn_qs.filter(transaction_type="Debit").aggregate(t=Sum("amount"))["t"] or 0
    )

    top_billers = (
        billing_qs.values("user__full_name", "user__role")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("-total")[:8]
    )

    return render(
        request,
        "white_label_dashboard/reports.html",
        _wl_context(
            request,
            role_breakdown=role_breakdown,
            billing_summary=billing_summary,
            paid_count=paid_count,
            unpaid_count=unpaid_count,
            credit_total=credit_total,
            debit_total=debit_total,
            top_billers=top_billers,
            total_users=subtree.count(),
        ),
    )


@login_required
@role_required(["white_label_admin"])
def white_label_banking(request):
    if not _require_tenant(request.user):
        return redirect("logout")

    try:
        access_request = BankingPortalAccessRequest.objects.get(user=request.user)
    except BankingPortalAccessRequest.DoesNotExist:
        access_request = None
        if request.method == "POST":
            access_request = BankingPortalAccessRequest.objects.create(user=request.user)
            messages.success(request, "Banking portal access request submitted.")
            return redirect("white_label_banking")

    return render(
        request,
        "white_label_dashboard/banking.html",
        _wl_context(request, access_request=access_request),
    )
