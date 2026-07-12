import os
import qrcode
from config import Config

def generate_product_qr(product_id):
    """
    Generates a QR code image for a given product ID and saves it to the QR codes directory.
    Returns the relative path to the saved image (from static/).
    """
    # Ensure config folder is initialized
    Config.init_app()
    
    # Create the QR Code object
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(product_id)
    qr.make(fit=True)

    # Create the image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Define filename and path
    filename = f"{product_id}.png"
    filepath = os.path.join(Config.QRCODE_FOLDER, filename)
    
    # Save the image
    img.save(filepath)
    
    # Return path relative to static/
    return f"qrcodes/{filename}"
