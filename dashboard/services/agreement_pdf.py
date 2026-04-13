import os
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    Image as RLImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


def _escape_xml(text):
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _draw_corner_signature(canv: pdfcanvas.Canvas, doc):
    w, h = A4
    margin = 14 * mm
    sig_path = getattr(doc, "_agreement_sig_path", None)
    name = getattr(doc, "_agreement_signer_name", "")
    dt = getattr(doc, "_agreement_sign_date", "")
    canv.saveState()
    box_w, box_h = 52 * mm, 18 * mm
    x = w - margin - box_w
    y = margin
    if sig_path and os.path.isfile(sig_path):
        try:
            canv.drawImage(
                sig_path,
                x,
                y,
                width=box_w - 28 * mm,
                height=box_h - 4 * mm,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass
    canv.setFillColor(colors.HexColor("#333333"))
    canv.setFont("Helvetica", 8)
    canv.drawRightString(w - margin, y + box_h + 7, (name or "")[:48])
    canv.drawRightString(w - margin, y + box_h - 3, dt or "")
    canv.restoreState()


def build_signed_agreement_pdf(
    *,
    terms_text: str,
    agreement_version: str,
    signer_name: str,
    typed_name: str,
    signature_image_path: str,
    accepted_at_display: str,
    ip_address: str,
    user_agent: str,
    user_email: str,
    branch_id: str,
) -> bytes:
    buf = BytesIO()
    # Extra top/right margin so corner signature + name/date do not overlap body text
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=38 * mm,
        title=f"Agreement v{agreement_version}",
    )
    doc._agreement_sig_path = signature_image_path
    doc._agreement_signer_name = typed_name or signer_name
    doc._agreement_sign_date = accepted_at_display

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "AgTitle",
        parent=styles["Heading1"],
        fontSize=14,
        spaceAfter=10,
        textColor=colors.HexColor("#0d47a1"),
    )
    body = ParagraphStyle(
        "AgBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        spaceAfter=6,
    )

    story = []
    story.append(Paragraph(_escape_xml("Terms & Conditions"), title_style))
    story.append(
        Paragraph(
            _escape_xml(
                f"Version {agreement_version} — Signatory (typed): {typed_name or signer_name} — Account: {user_email}"
            ),
            body,
        )
    )
    story.append(Spacer(1, 6 * mm))

    for block in terms_text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        story.append(Paragraph(_escape_xml(block), body))
        story.append(Spacer(1, 2 * mm))

    story.append(PageBreak())
    story.append(Paragraph(_escape_xml("Digital acceptance record"), title_style))
    story.append(Spacer(1, 4 * mm))
    if signature_image_path and os.path.isfile(signature_image_path):
        story.append(
            RLImage(
                signature_image_path,
                width=80 * mm,
                height=28 * mm,
                kind="proportional",
            )
        )
        story.append(Spacer(1, 4 * mm))

    audit_lines = [
        f"Typed name: {typed_name or signer_name}",
        f"Legal / profile name: {signer_name}",
        f"Email: {user_email}",
        f"Branch / ID: {branch_id or '—'}",
        f"Agreement version: {agreement_version}",
        f"Accepted at (server): {accepted_at_display}",
        f"IP address: {ip_address or '—'}",
        f"Device / User-Agent: {(user_agent or '')[:900]}",
        "",
        "Digitally accepted: The signatory confirmed reading the Terms & Conditions, "
        "entered their name, and applied the electronic signature above through this portal.",
    ]
    for line in audit_lines:
        story.append(Paragraph(_escape_xml(line), body))

    doc.build(story, onFirstPage=_draw_corner_signature, onLaterPages=_draw_corner_signature)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes
