from PIL import Image
from django.core.files.base import File
from io import BytesIO

"""_summary_: # Resize only if image dimensions exceed 150x150_
"""
def resize_profile_image(profile_image):
    img = Image.open(profile_image)
    if img.height > 150 or img.width > 150:
        output = BytesIO()
        img = img.resize((150, 150), Image.LANCZOS) # Replacing ANTIALIAS with LANCZOS
        img.save(output, format="PNG") 
        output.seek(0)
        return File(output, profile_image.name)  # Return a Django file object so it can be saved directly
    return profile_image