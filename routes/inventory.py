from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
import base64
import numpy as np
import cv2
from routes.auth import login_required
from models.product import Product
from models.inventory import Inventory

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/')
@login_required()
def index():
    # Fetch inventory transaction log
    transactions = Inventory.get_transactions(limit=100)
    # Fetch products list to populate the manual adjustment select dropdown
    products = Product.get_all()
    return render_template(
        'inventory.html',
        active_page='inventory',
        transactions=transactions,
        products=products
    )

@inventory_bp.route('/adjust', methods=['POST'])
@login_required()
def adjust_stock():
    product_id = request.form.get('product_id')
    tx_type = request.form.get('type') # IN, OUT, ADJUST
    quantity = int(request.form.get('quantity', 0))
    user_id = session.get('user_id')

    if not product_id or not tx_type or quantity <= 0:
        flash("Invalid product details or adjustment amount.", "error")
        return redirect(url_for('inventory.index'))

    # Restrict direct 'ADJUST' (stock reconciliation) to Admins & Managers
    if tx_type == 'ADJUST' and session.get('user_role') not in ['Admin', 'Manager']:
        flash("Access Denied: Only Admin and Managers can manually override stock counts.", "error")
        return redirect(url_for('inventory.index'))

    # Call product stock adjust model method
    success, message = Product.adjust_stock(product_id, tx_type, quantity, user_id)
    if success:
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(url_for('inventory.index'))

@inventory_bp.route('/scanner')
@login_required()
def scanner_page():
    return render_template('scanner.html', active_page='scanner')

@inventory_bp.route('/scan-frame', methods=['POST'])
@login_required()
def scan_frame():
    """
    AJAX endpoint that receives a base64 frame from client-side webcam,
    converts it to a CV2 image, and decodes it using OpenCV.
    """
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"success": False, "message": "No image frame received."})

        # Parse base64 string
        img_data = data['image'].split(',')[1]
        img_bytes = base64.b64decode(img_data)
        
        # Convert to numpy array and decode image using OpenCV
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"success": False, "message": "Failed to parse image frame."})

        # Initialize OpenCV QR Code Detector
        detector = cv2.QRCodeDetector()
        data_decoded, points, _ = detector.detectAndDecode(img)

        if data_decoded:
            # QR code decoded! Look up product
            product = Product.get_by_id(data_decoded)
            if product:
                return jsonify({
                    "success": True,
                    "product_id": product['id'],
                    "product_name": product['product_name'],
                    "current_qty": product['quantity'],
                    "shelf_id": product['shelf_id'] or 'Unassigned'
                })
            else:
                return jsonify({
                    "success": False,
                    "message": f"QR Code matches ID '{data_decoded}' but no matching product exists in the system."
                })

        return jsonify({"success": False, "message": "No QR code detected."})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
