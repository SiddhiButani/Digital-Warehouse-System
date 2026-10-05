from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from routes.auth import login_required
from models.product import Product
from models.supplier import Supplier
from models.warehouse import Warehouse
from models.inventory import Inventory

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
@login_required()
def index():
    products = Product.get_all()
    # Fetch shelves and suppliers for the "Add Product" form modal
    shelves = Warehouse.get_all_shelves()
    suppliers = Supplier.get_all()
    return render_template(
        'products.html',
        active_page='products',
        products=products,
        shelves=shelves,
        suppliers=suppliers
    )

@products_bp.route('/add', methods=['GET', 'POST'])
@login_required(roles=['Admin', 'Manager'])
def add_product():
    if request.method == 'POST':
        product_id = (request.form.get('product_id') or '').strip().upper()
        product_name = (request.form.get('product_name') or '').strip()
        category = (request.form.get('category') or '').strip()
        
        try:
            quantity = int(request.form.get('quantity') or 0)
            unit_price = float(request.form.get('unit_price') or 0.0)
        except (ValueError, TypeError):
            flash("Quantity and Unit Price must be valid numbers.", "error")
            return redirect(url_for('products.index'))

        if quantity < 0 or unit_price < 0:
            flash("Quantity and Unit Price cannot be negative.", "error")
            return redirect(url_for('products.index'))

        shelf_id = request.form.get('shelf_id')
        supplier_id = request.form.get('supplier_id')

        # Convert empty strings to None for DB insert
        shelf_id = None if not shelf_id else shelf_id
        supplier_id = None if not supplier_id else int(supplier_id)

        if not product_id or not product_name or not category:
            flash("Product ID, Name, and Category are required.", "error")
            return redirect(url_for('products.index'))

        user_id = session.get('user_id', 1)

        success, message = Product.create_product(
            product_id, product_name, category, quantity, unit_price, shelf_id, supplier_id, user_id=user_id
        )

        if success:
            flash(message, "success")
        else:
            flash(message, "error")

    return redirect(url_for('products.index'))

@products_bp.route('/edit/<product_id>', methods=['GET', 'POST'])
@login_required(roles=['Admin', 'Manager'])
def edit_product(product_id):
    product = Product.get_by_id(product_id)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for('products.index'))

    if request.method == 'POST':
        product_name = request.form.get('product_name').strip()
        category = request.form.get('category').strip()
        unit_price = float(request.form.get('unit_price', 0.0))
        shelf_id = request.form.get('shelf_id')
        supplier_id = request.form.get('supplier_id')

        # Convert empty strings to None for DB insert
        shelf_id = None if shelf_id == "" else shelf_id
        supplier_id = None if supplier_id == "" else int(supplier_id)

        if not product_name or not category:
            flash("Product Name and Category are required.", "error")
            return redirect(url_for('products.edit_product', product_id=product_id))

        success, message = Product.update_product(
            product_id, product_name, category, unit_price, shelf_id, supplier_id
        )

        if success:
            flash(message, "success")
            return redirect(url_for('products.view_product', product_id=product_id))
        else:
            flash(message, "error")

    shelves = Warehouse.get_all_shelves()
    suppliers = Supplier.get_all()
    return render_template(
        'product_detail.html',
        active_page='products',
        product=product,
        edit_mode=True,
        shelves=shelves,
        suppliers=suppliers
    )

@products_bp.route('/delete/<product_id>', methods=['POST'])
@login_required(roles=['Admin', 'Manager'])
def delete_product(product_id):
    success, message = Product.delete_product(product_id)
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for('products.index'))

@products_bp.route('/view/<product_id>')
@login_required()
def view_product(product_id):
    product = Product.get_by_id(product_id)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for('products.index'))

    transactions = Inventory.get_transactions_by_product(product_id)
    return render_template(
        'product_detail.html',
        active_page='products',
        product=product,
        edit_mode=False,
        transactions=transactions
    )
