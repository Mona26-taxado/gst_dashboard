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
import random
import string
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
from django.core.cache import cache
from django.conf import settings

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


def generate_simple_captcha():
    """Generate a simple captcha for testing"""
    try:
        # Generate 6 random characters
        captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Create a larger image for better visibility
        width, height = 300, 80  # Increased from 200x60 to 300x80
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Just draw the text in black with larger font
        try:
            # Try to use a larger font
            font = ImageFont.truetype("arial.ttf", 36)  # Increased from default to 36
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # Center the text
        text_x = (width - len(captcha_text) * 20) // 2  # Increased spacing
        text_y = (height - 36) // 2
        
        draw.text((text_x, text_y), captcha_text, fill='black', font=font)
        
        # Convert to base64
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        result = f"data:image/png;base64,{img_str}"
        
        return captcha_text, result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e


def generate_dynamic_captcha():
    """Generate a dynamic captcha with random numbers and letters"""
    try:
        # Generate 6 random characters (mix of numbers and letters)
        captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Create a larger image for better visibility
        width, height = 300, 80  # Increased from 200x60 to 300x80
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Add some noise (dots) to make it harder to read
        for _ in range(150):  # Increased noise
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.point((x, y), fill='lightgray')
        
        # Add lines for more noise
        for _ in range(8):  # Increased lines
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill='lightgray', width=1)
        
        # Try to use a font, fallback to default if not available
        try:
            # Try to use a larger font
            font = ImageFont.truetype("arial.ttf", 36)  # Increased from 24 to 36
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # Draw the captcha text
        text_width = draw.textlength(captcha_text, font=font) if font else len(captcha_text) * 20
        text_x = (width - text_width) // 2
        text_y = (height - 36) // 2
        
        # Draw each character with slight rotation and different colors
        for i, char in enumerate(captcha_text):
            char_x = text_x + (i * 45)  # Increased spacing between characters
            char_y = text_y + random.randint(-8, 8)  # Increased vertical variation
            
            # Random color for each character
            color = random.choice(['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'])
            draw.text((char_x, char_y), char, fill=color, font=font)
        
        # Convert to base64 for embedding in HTML
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        result = f"data:image/png;base64,{img_str}"
        
        return captcha_text, result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e

def verify_captcha(user_input, session_captcha):
    """Verify the captcha input against the session stored captcha"""
    if not user_input or not session_captcha:
        return False
    return user_input.upper() == session_captcha.upper()

