from flask import Blueprint, render_template, redirect, url_for, request, flash
from routes.auth import login_required
from models.supplier import Supplier

supplier_bp = Blueprint('suppliers', __name__)

@supplier_bp.route('/')
@login_required(roles=['Admin', 'Manager'])
def index():
    suppliers = Supplier.get_all()
    stats = Supplier.get_summary_stats()
    performance_map = {p['id']: p for p in stats.get('performance', [])}
    return render_template(
        'suppliers.html',
        active_page='suppliers',
        suppliers=suppliers,
        performance_map=performance_map,
        editing_supplier_id=None
    )

@supplier_bp.route('/add', methods=['POST'])
@login_required(roles=['Admin', 'Manager'])
def add_supplier():
    company_name = request.form.get('company_name').strip()
    contact_person = request.form.get('contact_person').strip()
    phone = request.form.get('phone').strip()
    email = request.form.get('email').strip()
    address = request.form.get('address').strip()

    if not company_name or not contact_person or not phone or not email or not address:
        flash("All fields are required to register a supplier.", "error")
        return redirect(url_for('suppliers.index'))

    success, message, _ = Supplier.create(company_name, contact_person, phone, email, address)
    if success:
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(url_for('suppliers.index'))

@supplier_bp.route('/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required(roles=['Admin', 'Manager'])
def edit_supplier(supplier_id):
    if request.method == 'POST':
        company_name = request.form.get('company_name').strip()
        contact_person = request.form.get('contact_person').strip()
        phone = request.form.get('phone').strip()
        email = request.form.get('email').strip()
        address = request.form.get('address').strip()

        if not company_name or not contact_person or not phone or not email or not address:
            flash("All fields are required.", "error")
            return redirect(url_for('suppliers.edit_supplier', supplier_id=supplier_id))

        success, message = Supplier.update(supplier_id, company_name, contact_person, phone, email, address)
        if success:
            flash(message, "success")
            return redirect(url_for('suppliers.index'))
        else:
            flash(message, "error")

    # If GET, render page with this specific supplier in edit mode in the side form
    suppliers = Supplier.get_all()
    stats = Supplier.get_summary_stats()
    performance_map = {p['id']: p for p in stats.get('performance', [])}
    
    current_supplier = Supplier.get_by_id(supplier_id)
    if not current_supplier:
        flash("Supplier not found.", "error")
        return redirect(url_for('suppliers.index'))

    return render_template(
        'suppliers.html',
        active_page='suppliers',
        suppliers=suppliers,
        performance_map=performance_map,
        editing_supplier_id=supplier_id,
        current_supplier=current_supplier
    )

@supplier_bp.route('/delete/<int:supplier_id>', methods=['POST'])
@login_required(roles=['Admin', 'Manager'])
def delete_supplier(supplier_id):
    success, message = Supplier.delete(supplier_id)
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for('suppliers.index'))
