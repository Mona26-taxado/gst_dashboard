from PIL import Image
import os

# Create icons directory if it doesn't exist
os.makedirs('static/icons', exist_ok=True)

# Open the logo image
logo = Image.open('logo.png')  # Make sure your logo is saved as logo.png in the same directory

# Convert to RGBA if not already
logo = logo.convert('RGBA')

# Create 192x192 version
icon_192 = logo.resize((192, 192), Image.Resampling.LANCZOS)
icon_192.save('static/icons/icon-192x192.png', 'PNG')

# Create 512x512 version
icon_512 = logo.resize((512, 512), Image.Resampling.LANCZOS)
icon_512.save('static/icons/icon-512x512.png', 'PNG')

print("Icons generated successfully!") 