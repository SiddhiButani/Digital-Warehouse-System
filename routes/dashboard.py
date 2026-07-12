from flask import Blueprint, render_template, session
from routes.auth import login_required
from models.product import Product
from models.supplier import Supplier
from models.warehouse import Warehouse
from models.inventory import Inventory

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required()
def index():
    # 1. Fetch KPI metrics
    stats = Product.get_summary_stats()
    supplier_stats = Supplier.get_summary_stats()
    stats['total_suppliers'] = supplier_stats['total_suppliers']
    
    # 2. Fetch occupancy information
    zone_utilization = Warehouse.get_zone_utilization()
    
    # 3. Fetch recent inventory transactions (last 8)
    recent_transactions = Inventory.get_transactions(limit=8)
    
    # 4. Fetch low-stock items (quantity <= 10)
    low_stock_items = Product.get_low_stock(threshold=10)
    
    return render_template(
        'dashboard.html',
        active_page='dashboard',
        stats=stats,
        zone_utilization=zone_utilization,
        recent_transactions=recent_transactions,
        low_stock_items=low_stock_items
    )
