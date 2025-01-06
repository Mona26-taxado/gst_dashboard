from django.shortcuts import redirect
from functools import wraps


import logging

logger = logging.getLogger(__name__)

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                logger.info("User is not authenticated. Redirecting to login.")
                return redirect('login')

            if request.user.role not in allowed_roles:
                logger.warning(f"Unauthorized access attempt by user: {request.user.username}, Role: {request.user.role}")
                return redirect('not_authorized')

            logger.info(f"Access granted for user: {request.user.username}, Role: {request.user.role}")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator





import qrcode
import os

def generate_qr(user_name, upi_id="9336323478@okbizaxis"):
    qr_data = f"upi://pay?pa={upi_id}&pn={user_name}&cu=INR"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Correctly locate the QR folder
    qr_folder = os.path.join('dashboard', 'static', 'qr_codes')
    os.makedirs(qr_folder, exist_ok=True)

    qr_filename = f"{user_name.replace(' ', '_')}_qr.png"
    qr_path = os.path.join(qr_folder, qr_filename)
    qr.make_image(fill="black", back_color="white").save(qr_path)

    # Return the path relative to the 'static' directory
    return f"qr_codes/{qr_filename}"

