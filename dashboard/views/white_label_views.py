"""White Label Admin dashboard — reuses GSK patterns with tenant scoping."""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from dashboard.forms import AddGSKForm
from dashboard.models import CustomUser, Transaction, Wallet
from dashboard.tenant import WL_CHILD_ROLES, wl_admin_subtree_qs
from dashboard.utils import role_required
from dashboard.wallet_ops import WalletError, transfer_wallet


def _require_tenant(user):
    if not user.tenant_id:
        return False
    return True


def _wl_context(request, **extra):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    ctx = {
        "wallet_balance": wallet.balance,
        "tenant": request.user.tenant or getattr(request, "tenant", None),
    }
    ctx.update(extra)
    return ctx


@login_required
@role_required(["white_label_admin"])
def white_label_dashboard(request):
    if not _require_tenant(request.user):
        messages.error(request, "No tenant linked to your account.")
        return redirect("logout")

    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    subtree = wl_admin_subtree_qs(request.user)
    context = _wl_context(
        request,
        total_users=subtree.count(),
        total_md=subtree.filter(role="master_distributor").count(),
        total_distributors=subtree.filter(role="distributor").count(),
        total_retailers=subtree.filter(role="retailer").count(),
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
    else:
        form = AddGSKForm(allowed_roles=allowed)

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
    users = wl_admin_subtree_qs(request.user).order_by("-created_at")
    if search_query:
        users = users.filter(
            Q(full_name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(branch_id__icontains=search_query)
        )

    paginator = Paginator(users, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "white_label_dashboard/view_users.html",
        _wl_context(
            request,
            page_obj=page_obj,
            search_query=search_query,
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

    tenant_user_ids = CustomUser.objects.filter(
        tenant_id=request.user.tenant_id
    ).values_list("id", flat=True)

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
