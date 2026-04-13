"""
Agreement text + placeholders.

Placeholders in admin or default text (replaced at view/PDF time):
  {{DATE}} = user account / ID first created (created_at); {{NAME}} {{USER_ID}} {{AMOUNT}} {{IP_ADDRESS}} {{DEVICE}}
  {{ADDRESS}} {{MOBILE}} {{STATE}}

Custom body: Django Admin → Portal agreement text (overrides default).

Bump AGREEMENT_VERSION when legal text or meaning changes (users must re-sign).
"""

from django.conf import settings
from django.utils import timezone

AGREEMENT_VERSION = "2.0"


def _user_first_account_datetime(user):
    """Date/time when the portal user record was first created (ID / account)."""
    dt = getattr(user, "created_at", None)
    if not dt and hasattr(user, "date_joined"):
        dt = user.date_joined
    if not dt:
        dt = timezone.now()
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def fill_agreement_placeholders(
    text,
    user,
    request=None,
    *,
    typed_name=None,
):
    """Replace {{DATE}}, {{NAME}}, etc. Plain text only; unknown {{tags}} are left unchanged."""
    if not text:
        return ""

    date_str = timezone.localtime(_user_first_account_datetime(user)).strftime("%d %B %Y")

    name = (typed_name or getattr(user, "full_name", None) or user.get_full_name() or user.email or "").strip()
    uid = ""
    if getattr(user, "branch_id", None):
        uid = str(user.branch_id).strip()
    if not uid:
        uid = str(user.pk)

    amount_display = "____________"
    invoice_amount = None
    try:
        reg_invoice = getattr(user, "registration_invoice", None)
        if reg_invoice and getattr(reg_invoice, "amount", None) is not None:
            invoice_amount = reg_invoice.amount
    except Exception:
        invoice_amount = None

    if invoice_amount is not None and str(invoice_amount).strip():
        amount_display = f"INR {invoice_amount}"
    else:
        disp = getattr(settings, "AGREEMENT_FRANCHISE_FEE_DISPLAY", None)
        if disp and str(disp).strip():
            amount_display = str(disp).strip()
        else:
            raw_fee = getattr(settings, "AGREEMENT_FRANCHISE_FEE", None)
            if raw_fee is not None and str(raw_fee).strip():
                amount_display = f"INR {str(raw_fee).strip()}"

    ip = "—"
    device = "—"
    if request is not None:
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            ip = xff.split(",")[0].strip()[:45]
        else:
            ip = (request.META.get("REMOTE_ADDR") or "—")[:45]
        device = (request.META.get("HTTP_USER_AGENT") or "—")[:900]

    user_address = (getattr(user, "address", None) or "").strip() or "—"
    user_mobile = (getattr(user, "mobile_number", None) or "").strip() or "—"
    user_state = (getattr(user, "state", None) or "").strip() or "—"

    mapping = {
        "{{DATE}}": date_str,
        "{{NAME}}": name or "—",
        "{{USER_ID}}": uid,
        "{{AMOUNT}}": amount_display,
        "{{ADDRESS}}": user_address,
        "{{MOBILE}}": user_mobile,
        "{{STATE}}": user_state,
        "{{IP_ADDRESS}}": ip,
        "{{DEVICE}}": device,
    }
    out = str(text)
    for key, val in mapping.items():
        out = out.replace(key, val)
    return out


def _built_in_default_terms():
    return """
Service-Level-Agreement
Customer Name: {{NAME}}
Address: {{ADDRESS}}
Mobile no.: {{MOBILE}}
Date: {{DATE}}

TAXADO TECHNOLOGY PRIVATE LIMITED
385 HIGC, Sidharth Enclave, Taramandal,
Gorakhpur, Uttar Pardesh - 273001.

Subject: Franchise Agreement

Dear Taxado Technology Private Limited,

I am writing to express my interest in entering into a franchise agreement with TAXADO TECHNOLOGY PRIVATE LIMITED for the operation of a GRAHAK SAHAAYATA KENDRA franchise. As per our discussions and negotiations, I believe this agreement will provide a mutually beneficial opportunity for both parties.

I have thoroughly reviewed the franchise disclosure document and other relevant materials provided by TAXADO TECHNOLOGY PRIVATE LIMITED, and I am confident in the potential success of the GRAHAK SAHAAYATA KENDRA franchise in my desired location.

To proceed with the franchise, I would like to propose the following terms and conditions for the franchise agreement:

1. Territory:
- The designated territory for the franchise will be {{STATE}}.
- This territory will be exclusive, ensuring that no other franchises of GRAHAK SAHAAYATA KENDRA will operate within the designated area.

2. Franchise Fee and Payments:
- I am prepared to pay a franchise fee of {{AMOUNT}} (ID fee as mentioned in your invoice) upon the execution of this agreement.
- These fees will be paid on a franchise basis.

3. Initial Term and Renewal:
- The initial term of the franchise agreement will be 25 Years of License, commencing on {{DATE}}.
- Upon the expiration of the initial term, both parties may have the option to renew the agreement for subsequent terms of 25 Year.
- The terms and conditions of any renewal will be negotiated in good faith between both parties.

4. Training and Support:
- TAXADO TECHNOLOGY PRIVATE LIMITED agrees to provide comprehensive training and support to ensure the successful operation of the franchise.
- This training will cover all aspects of TAXADO TECHNOLOGY PRIVATE LIMITED business operations, including product knowledge, marketing strategies, and operational procedures.
- The initial training will take place at a location designated by TAXADO TECHNOLOGY PRIVATE LIMITED for a duration of 1 hours.
- Ongoing support will be available through regular communication channels, training materials, and assistance in resolving operational challenges.

5. Branding and Marketing:
- I agree to use the approved branding and marketing materials provided by TAXADO TECHNOLOGY PRIVATE LIMITED in the operation of the franchise.

6. Obligations and Responsibilities:
- I will diligently operate the franchise in accordance with the standards, procedures, and guidelines set forth by TAXADO TECHNOLOGY PRIVATE LIMITED.
- I will maintain proper staffing, adhere to quality control measures, and provide excellent customer service.
- I will promptly report and address any operational issues or concerns that may arise.
- I will maintain accurate records of sales, expenses, and other financial data as required by TAXADO TECHNOLOGY PRIVATE LIMITED.

7. Termination:
- Either party may terminate this agreement upon providing 25 Year written notice to the other party.
- Termination may occur in the event of a material breach of the franchise agreement, failure to meet performance standards, or other specified circumstances as outlined in the agreement.
- The specific circumstances under which an amount may be deemed non-refundable can vary depending on the terms and conditions set by the company. It's important for customers to carefully read and understand the terms and conditions or any agreements they enter into with a company to be aware of any non-refundable amounts.
- Certain services: Some services, such as consultations, professional advice, or specialized services, may be subject to non-refundable fees due to the time and expertise involved. If the customer cancels or decides not to proceed with the service, the company may retain the non-refundable portion of the payment.
- It's crucial for both companies and customers to have clear communication and understanding regarding non-refundable amounts to avoid any misunderstandings or disputes.

8. Services:
The Service Provider agrees to provide the following services to the Client by GRAHAK SAHAAYATA KENDRA:
Pan Card, GST Registration, Ration Card, Government to Citizens Service, Voter Id, Flight & Hotel Booking, Money Transfer, Aadhar Update (we refuse the service of linking number in Aadhaar), Aadhar Enable Payment System (AEPS), Insurance, Banking Related Services, and 250+ more Services......

9. Governing Law and Dispute Resolution:
This Agreement shall be governed by and construed in accordance with the laws of . Any disputes arising out of or relating to this Agreement shall be resolved through good-faith negotiations between the Parties. If the Parties are unable to reach a resolution, the dispute shall be referred to mediation or arbitration in accordance with the laws of [Jurisdiction].

10. Entire Agreement:
This Agreement constitutes the entire understanding and agreement between the Parties and supersedes any prior agreements, whether written or oral, relating to the subject matter herein.

11. Amendment and Waiver:
Any amendment or waiver of this Agreement must be in writing and signed by both Parties.

Please indicate your acceptance of the terms and conditions outlined in this Agreement by signing below. This Agreement may be executed in counterparts, each of which shall be deemed an original, but all of which together shall constitute one and the same instrument.

This letter represents a preliminary proposal for the franchise agreement, and I am open to further negotiations and discussions to finalize the terms and conditions. I kindly request your review and consideration of the proposed terms. If you agree, I would be grateful if you could provide a franchise agreement draft based on these terms, or suggest any modifications or additions that you deem necessary.

Thank you for considering my application. I look forward to the opportunity to become a valued franchisee of Taxado Technology Private Limited. Should you require any additional information or documentation, please do not hesitate to contact me.

12. Terms and Conditions:
These Terms and Conditions govern your use of our website and services. By accessing or using our services, you agree to be bound by these terms.

Acceptance of Terms
By accessing and using Grahak Sahaayata Kendra's website and services, you acknowledge that you have read, understood, and agree to be bound by these Terms and Conditions. If you do not agree to these terms, please do not use our services.

Services Description
Grahak Sahaayata Kendra provides various services including but not limited to:
- Aadhar card services (correction, update, etc.)
- PAN card services
- Bill payments and utility services
- Government document processing
- Other digital and financial services

User Responsibilities
As a user of our services, you agree to:
- Provide accurate and complete information
- Maintain the confidentiality of your account credentials
- Use the services in compliance with applicable laws
- Not engage in any fraudulent or unauthorized activities
- Not interfere with the proper functioning of our services

Service Fees and Payments
Our service fees are clearly displayed before the completion of any transaction. By using our services, you agree to pay all applicable fees and charges. We reserve the right to modify our fee structure with prior notice.

Intellectual Property
All content, logos, trademarks, and other intellectual property on our website are owned by Grahak Sahaayata Kendra and are protected by applicable copyright and trademark laws. You may not use our intellectual property without our express written permission.

Limitation of Liability
Grahak Sahaayata Kendra shall not be liable for any indirect, incidental, special, consequential, or punitive damages resulting from your use or inability to use our services. Our liability is limited to the amount paid for the specific service in question.

Service Modifications
We reserve the right to modify, suspend, or discontinue any aspect of our services at any time without prior notice. We shall not be liable to you or any third party for any modification, suspension, or discontinuance of services.

Governing Law
These Terms and Conditions shall be governed by and construed in accordance with the laws of India. Any disputes arising from these terms shall be subject to the exclusive jurisdiction of the courts in Gorakhpur, Uttar Pradesh.

Changes to Terms
We reserve the right to modify these Terms and Conditions at any time. We will notify users of any material changes by posting the updated terms on our website. Your continued use of our services after such modifications constitutes your acceptance of the updated terms.

13. Privacy Policy:
This Privacy Policy explains how we collect, use, disclose, and safeguard your personal information when you visit or use our Service.

Information We Collect
1.1 Personal Information You Provide
- Contact data: name, email address, postal address, phone number
- Account information: user ID, login credentials
- Service details: information you submit when availing services (Aadhaar correction, PAN card, BBPS, AEPS, etc.)
- Payment details: transaction IDs, billing information

1.2 Information Collected Automatically
- Usage data: pages viewed, time spent, bounce rate, clicks
- Device & browser data: IP address, device type, operating system, browser type
- Cookies & tracking: session cookies, persistent cookies, web beacons

1.3 Third-Party Sources
- Analytics providers (e.g., Google Analytics)
- Advertising partners (e.g., Meta Ads)
- Payment gateways

How We Use Your Information
We use collected data to:
1. Provide & improve services - Process service requests, manage your account, deliver customer support
2. Communicate - Send confirmations, updates, marketing messages (with opt-out)
3. Analyze & optimize - Monitor usage, diagnose technical issues, generate insights
4. Legal & safety - Comply with laws, prevent fraud, enforce our Terms

Cookies & Tracking Technologies
We use cookies and similar technologies to personalize your experience and analyze traffic. You can manage or disable cookies in your browser settings; however, some features may not function properly if cookies are blocked.

Disclosure of Your Information
We may share your data with:
- Service providers who perform functions on our behalf (hosting, payment processing, analytics)
- Affiliates within our corporate group for operational purposes
- Legal authorities if required by law or to protect rights, safety, or property
- Business transfers in connection with a merger, acquisition, or sale

Data Security & Retention
We implement reasonable technical and organizational measures (encryption, access controls) to protect your data. Your personal information is retained only as long as necessary to fulfill the purposes described herein, comply with legal obligations, resolve disputes, and enforce our agreements.

Your Rights
Depending on applicable law, you may have the right to:
- Access the personal data we hold about you
- Correct or update inaccurate information
- Delete your personal data ("right to be forgotten")
- Object to or restrict processing of your data
- Portability: receive your data in a structured, machine-readable format
- Withdraw consent where processing is based on consent

To exercise any of these rights, please contact us at privacy@grahaksahaayatakendra.com.

Children's Privacy
Our Service is not directed to children under 18. We do not knowingly collect personal data from minors. If you believe we have inadvertently collected data from a child, please contact us to have it deleted.

Changes to This Policy
We may update this Privacy Policy from time to time. We will notify you of material changes by posting the new policy on this page with a revised "Last updated" date.

14. Refund and Return Policy:
This Refund & Return Policy outlines when and how you may request refunds or returns, and the process we follow to address them.

Scope
1. Services Covered
- Aadhaar correction
- PAN card application
- BBPS (bill payment) services
- AEPS (banking transactions)
- GST registration
- Other government-related services

2. Non-Refundable Items
- Government fees, statutory charges, and third-party processing fees once paid
- Partially completed services where updates have already been submitted to authorities
- Wallet balance is non-refundable.
- Once the payment is made for services, the amount paid is non-refundable (except as specified below).

License Fee & Wallet Refund Policy
Important Information:
- License Fee: License fee is refundable subject to our refund policy terms and conditions.
- Wallet Balance: Wallet balance is non-refundable. Once money is added to your wallet, it cannot be refunded. Wallet balance can only be used for availing services on our platform.

Please ensure you understand this policy before making any payments. Wallet topups are final and non-refundable.

Eligibility for Refund
You may request a refund if:
1. Service Not Rendered - We did not initiate or complete the service within the promised timeframe.
2. Duplicate Purchase - You inadvertently paid for the same service more than once.
3. Erroneous Charge - A billing error occurred on our end.

To initiate a refund request, you must contact us within 15 days of your transaction date.

Return of Documents
For services requiring document submission (e.g., physical forms, ID proofs):
- Return Request: If you wish to withdraw your application before processing begins, submit a written request within 7 days of document receipt.
- Return Method: We will return original documents via registered post or a secure courier at our expense.

Refund Process
1. Submit Request
Email us at support@grahaksahaayatakendra.com with:
- Service name & transaction ID
- Date of purchase
- Reason for refund
- License fee refund requests must include your license number and registration details

2. Verification
We will acknowledge receipt within 30 business days and may request additional information.

3. Approval & Processing
Once approved, refunds are processed and credited to your original payment method. Please note: The refund credit process may take up to 120 days (approximately 4 months) from the date of approval. This timeline includes verification, processing, and bank transfer procedures.

4. Refund Timeline
- Request acknowledgment: Within 30 business days
- Verification & approval: 30-60 business days
- Credit to your account: Up to 120 days from approval date

We appreciate your patience during the refund process. You will receive email notifications at each stage of the refund process.

Partial Refunds
If a service was partially delivered (e.g., application submitted but not approved), we may issue a pro-rated refund based on the amount of work completed, less any non-refundable fees. Note: License fee refunds are processed as per the refund timeline mentioned in Section 4.

Cancellations
- By You: You may cancel a service request before it enters the processing queue. A cancellation fee of 10% of service charges applies to cover administrative costs.
- By Us: We reserve the right to cancel any request due to incomplete documentation or non-compliance. In such cases, full refunds (minus third-party fees) will be issued.

Chargebacks
If you dispute a transaction with your bank or payment provider, we may suspend your account until the investigation is resolved. If the chargeback is found invalid, we reserve the right to recover the disputed amount and any associated fees.

15. Cancellation Policy:
This Cancellation Policy explains when and how you can cancel, any applicable fees, and our rights to cancel services.

Scope
This policy applies to all services offered through our platform (grahaksahaayatakendra.com), including Aadhaar correction, PAN card applications, BBPS payments, AEPS transactions, GST registration, and other government-related services.

Cancellation by You
1. Before Processing Begins
You may cancel any service request free of charge provided you submit your cancellation request in writing via email at support@grahaksahaayatakendra.com or call us at +91 551 796 0370 before we begin processing your documents.

2. After Processing Has Started
If you wish to cancel after we have initiated processing (e.g. forms submitted to authorities), a 10% cancellation fee of the service charge applies to cover administrative costs. Any government or third-party fees already paid remain non-refundable.

3. How to Cancel
- Email subject: "Cancellation Request - [Service Name] - [Transaction ID]"
- Include your name, contact number, transaction ID, and reason for cancellation.

Cancellation by Us
We reserve the right to cancel your service request (with full refund of service charges, excluding any non-refundable government or third-party fees) if:
- Your documentation is incomplete or invalid and remains uncorrected after our notice.
- We are unable to verify your identity or legality of documents.
- There is evidence of fraud or misuse of our services.
- We suspend services due to technical or regulatory reasons.

Effect of Cancellation
- Once cancellation is confirmed, we will stop all further processing.
- Any refunds due will be processed according to our Refund & Return Policy.
- We will confirm cancellation and refund status via email within 2 business days.

Non-Refundable & Non-Cancellable Items
- Government fees, statutory charges, and third-party processing fees are non-refundable and non-cancellable once paid.
- Once a payment is made for a service that has been fully completed, the amount is non-refundable.

Client Name: {{NAME}}
[Client's Signature]
Date: {{DATE}}
Yours sincerely,
TAXADO TECHNOLOGY PRIVATE LIMITED
""".strip()


def get_custom_agreement_body_from_db():
    """Return trimmed custom text from admin, or None if not configured."""
    try:
        from dashboard.models import PortalAgreementText

        row = PortalAgreementText.objects.order_by("-updated_at").first()
        if row and (row.terms_body or "").strip():
            return (row.terms_body or "").strip()
    except Exception:
        pass
    return None


def get_terms_plain_text():
    custom = get_custom_agreement_body_from_db()
    if custom:
        return custom
    return _built_in_default_terms()
