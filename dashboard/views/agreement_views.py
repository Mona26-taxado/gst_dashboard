import base64
import logging
import re
import uuid

from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.utils import timezone

from dashboard.agreement_content import (
    AGREEMENT_VERSION,
    fill_agreement_placeholders,
    get_terms_plain_text,
)
from dashboard.agreement_gate import AGREEMENT_REQUIRED_ROLES
from dashboard.models import AgreementAcceptance, CustomUser, Wallet
from dashboard.services.agreement_pdf import build_signed_agreement_pdf
from dashboard.utils import role_required

logger = logging.getLogger(__name__)

ALLOWED_ROLES = list(AGREEMENT_REQUIRED_ROLES)


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()[:45]
    return (request.META.get("REMOTE_ADDR") or "")[:45]


def _decode_signature_data_uri(data_uri: str) -> bytes:
    if not data_uri:
        return b""
    m = re.match(
        r"^data:image/(png|jpeg|jpg|webp);base64,(.+)$", data_uri.strip(), re.I | re.S
    )
    if not m:
        return b""
    try:
        return base64.b64decode(m.group(2))
    except Exception:
        return b""


def _pick_template(request):
    if request.user.role == "retailer_2":
        return "agreement/sign_agreement_csc.html"
    return "agreement/sign_agreement.html"


def _wallet_balance(user):
    try:
        return Wallet.objects.get(user=user).balance
    except Wallet.DoesNotExist:
        return 0


def _sign_context(request, **extra):
    ctx = {
        "wallet_balance": _wallet_balance(request.user),
    }
    ctx.update(extra)
    return ctx


def _delete_acceptance_files(acc: AgreementAcceptance):
    """Delete stored media files for old agreement rows."""
    try:
        if acc.signature_image:
            acc.signature_image.delete(save=False)
    except Exception:
        pass
    try:
        if acc.pdf_file:
            acc.pdf_file.delete(save=False)
    except Exception:
        pass


def _cleanup_old_acceptances(user, keep_id: int):
    """Keep only the latest acceptance row per user to reduce DB growth."""
    old_rows = AgreementAcceptance.objects.filter(user=user).exclude(pk=keep_id)
    for old in old_rows:
        _delete_acceptance_files(old)
    old_rows.delete()


@role_required(ALLOWED_ROLES)
def sign_agreement_view(request):
    terms_raw = get_terms_plain_text()
    existing = AgreementAcceptance.objects.filter(
        user=request.user, agreement_version=AGREEMENT_VERSION
    ).first()

    typed_name_input = ""
    if request.method == "POST":
        typed_name_input = (request.POST.get("typed_name") or "").strip()

    terms_display = fill_agreement_placeholders(
        terms_raw,
        request.user,
        request,
        typed_name=typed_name_input or None,
    )

    if request.method == "POST":
        if existing:
            messages.info(request, "You have already signed the current agreement version.")
            return redirect("sign_agreement")

        agree = request.POST.get("agree_terms")
        read_confirm = request.POST.get("read_confirm")
        typed_name = (request.POST.get("typed_name") or "").strip()
        signature_data = request.POST.get("signature_data") or ""
        upload = request.FILES.get("signature_upload")

        errors = []
        if agree != "on":
            errors.append("You must tick the box to confirm you have read and agree to the Terms & Conditions.")
        if read_confirm != "1":
            errors.append('Please use "Read full agreement" or scroll to the end of the terms before signing.')
        if len(typed_name) < 2:
            errors.append("Please type your full name as it appears on the agreement.")

        sig_bytes = b""
        if upload and upload.size > 0:
            if upload.size > 3 * 1024 * 1024:
                errors.append("Signature image must be under 3 MB.")
            else:
                sig_bytes = upload.read()
        if not sig_bytes:
            sig_bytes = _decode_signature_data_uri(signature_data)
        if len(sig_bytes) < 80:
            errors.append("Please draw your signature on the pad or upload a clear signature image.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(
                request,
                _pick_template(request),
                _sign_context(
                    request,
                    terms=terms_display,
                    agreement_version=AGREEMENT_VERSION,
                    existing=None,
                    typed_name_default=typed_name,
                ),
            )

        ip = _client_ip(request)
        ua = request.META.get("HTTP_USER_AGENT", "") or ""
        now = timezone.now()
        accepted_display = timezone.localtime(now).strftime("%d-%b-%Y %H:%M:%S %Z")

        try:
            with transaction.atomic():
                acc = AgreementAcceptance(
                    user=request.user,
                    agreement_version=AGREEMENT_VERSION,
                    ip_address=ip or "unknown",
                    user_agent=ua[:2000],
                    typed_name=typed_name,
                    email_sent_status="pending",
                )
                fname = f"sig_{request.user.id}_{uuid.uuid4().hex[:10]}.png"
                acc.signature_image.save(fname, ContentFile(sig_bytes), save=False)
                acc.save()
                acc.refresh_from_db()

                terms_for_pdf = fill_agreement_placeholders(
                    terms_raw,
                    request.user,
                    request,
                    typed_name=typed_name,
                )

                pdf_bytes = build_signed_agreement_pdf(
                    terms_text=terms_for_pdf,
                    agreement_version=AGREEMENT_VERSION,
                    signer_name=request.user.full_name or request.user.email,
                    typed_name=typed_name,
                    signature_image_path=acc.signature_image.path,
                    accepted_at_display=accepted_display,
                    ip_address=ip,
                    user_agent=ua,
                    user_email=request.user.email,
                    branch_id=request.user.branch_id or "",
                )
                pdf_name = f"agreement_{request.user.id}_{uuid.uuid4().hex[:12]}.pdf"
                acc.pdf_file.save(pdf_name, ContentFile(pdf_bytes), save=True)
                _cleanup_old_acceptances(request.user, keep_id=acc.id)

            email_ok = _send_agreement_emails(request.user, acc, pdf_bytes)
            request.session.pop("agreement_block_notice_shown", None)
            if email_ok:
                messages.success(
                    request,
                    "Your agreement has been signed. A copy has been emailed to you and to the administrator.",
                )
            else:
                acc.refresh_from_db(fields=["email_sent_status", "email_error"])
                messages.warning(
                    request,
                    "Your agreement was saved, but we could not send the email copy. "
                    "You can download the signed PDF from this page. If this continues, contact support.",
                )
            return redirect("sign_agreement")
        except Exception as exc:
            logger.exception("Agreement signing failed: %s", exc)
            messages.error(
                request,
                "We could not complete signing. Please try again or contact support if the problem continues.",
            )
            return render(
                request,
                _pick_template(request),
                _sign_context(
                    request,
                    terms=terms_display,
                    agreement_version=AGREEMENT_VERSION,
                    existing=None,
                    typed_name_default=typed_name,
                ),
            )

    return render(
        request,
        _pick_template(request),
        _sign_context(
            request,
            terms=terms_display,
            agreement_version=AGREEMENT_VERSION,
            existing=existing,
            typed_name_default=request.user.full_name or "",
        ),
    )


def _send_agreement_emails(user: CustomUser, acc: AgreementAcceptance, pdf_bytes: bytes) -> bool:
    """Email signed PDF to the user; BCC admin + CC list. Returns True if SMTP reported success."""
    from django.core.mail import EmailMessage

    admin_copy = getattr(settings, "AGREEMENT_ADMIN_NOTIFY_EMAIL", None) or settings.DEFAULT_FROM_EMAIL
    admin_cc_raw = getattr(settings, "AGREEMENT_ADMIN_NOTIFY_CC", "") or ""
    admin_cc_list = [email.strip() for email in str(admin_cc_raw).split(",") if email.strip()]
    subject = f"Signed agreement ({acc.agreement_version}) — {user.full_name or user.email}"
    body = (
        f"Agreement version {acc.agreement_version} was digitally signed on the portal.\n\n"
        f"User: {user.full_name} <{user.email}>\n"
        f"Typed name: {acc.typed_name}\n"
        f"Accepted at: {acc.accepted_at}\n"
        f"IP: {acc.ip_address}\n"
    )
    pdf_name = f"signed_agreement_{user.id}.pdf"

    try:
        signer_email = (user.email or "").strip()
        admin_norm = (admin_copy or "").strip()

        staff_bcc_raw = []
        for email in [admin_norm, *admin_cc_list]:
            e = (email or "").strip()
            if e and e not in staff_bcc_raw:
                staff_bcc_raw.append(e)

        if signer_email:
            to_emails = [signer_email]
            bcc_emails = [e for e in staff_bcc_raw if e.lower() != signer_email.lower()]
        elif admin_norm:
            # User has no email on file: deliver primary copy to admin inbox, rest as BCC.
            to_emails = [admin_norm]
            bcc_emails = [e for e in staff_bcc_raw if e.lower() != admin_norm.lower()]
        else:
            raise ValueError("No recipient addresses (user email empty and AGREEMENT_ADMIN_NOTIFY_EMAIL unset).")

        if not to_emails and not bcc_emails:
            raise ValueError("No recipient addresses configured for agreement email.")

        msg = EmailMessage(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            to_emails,
            bcc=bcc_emails,
        )
        msg.attach(pdf_name, pdf_bytes, "application/pdf")
        msg.send(fail_silently=False)
        acc.email_sent_status = "sent"
        acc.email_error = ""
        acc.save(update_fields=["email_sent_status", "email_error"])
        return True
    except Exception as exc:
        logger.exception("Agreement email failed: %s", exc)
        acc.email_sent_status = "failed"
        acc.email_error = str(exc)[:500]
        acc.save(update_fields=["email_sent_status", "email_error"])
        return False


@role_required(ALLOWED_ROLES)
def download_my_agreement(request, acceptance_id):
    acc = AgreementAcceptance.objects.filter(pk=acceptance_id, user=request.user).first()
    if not acc or not acc.pdf_file:
        raise Http404()
    return FileResponse(
        acc.pdf_file.open("rb"),
        as_attachment=True,
        filename=f"signed_agreement_v{acc.agreement_version}.pdf",
    )
