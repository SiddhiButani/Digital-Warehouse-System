from flask import Blueprint, render_template
import io
import base64
import pandas as pd
import numpy as np
import matplotlib
# Use the non-interactive Agg backend to run safely on Flask threads
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from routes.auth import login_required
from database.db import get_db_connection
from models.inventory import Inventory
from models.product import Product
from models.warehouse import Warehouse

analytics_bp = Blueprint('analytics', __name__)

def fig_to_base64(fig):
    """Converts a Matplotlib figure to a base64 encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor='none')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig) # Prevent memory leaks
    return f"data:image/png;base64,{img_str}"

def apply_chart_style(ax, title=""):
    """Applies custom dark-theme dashboard styles to a Matplotlib axes object."""
    ax.set_title(title, color='#f3f4f6', fontsize=14, pad=15, fontweight='bold', fontname='sans-serif')
    ax.set_facecolor('none')
    ax.tick_params(colors='#9ca3af', labelsize=9)
    ax.xaxis.label.set_color('#9ca3af')
    ax.yaxis.label.set_color('#9ca3af')
    
    # Hide top and right spines
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    
    # Style remaining spines
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color((1.0, 1.0, 1.0, 0.15))
        ax.spines[spine].set_linewidth(1)
        
    ax.grid(True, linestyle=':', alpha=0.15, color='#fff')

@analytics_bp.route('/')
@login_required()
def index():
    # Setup dark plot theme parameters globally
    plt.rcParams['text.color'] = '#f3f4f6'
    plt.rcParams['axes.labelcolor'] = '#9ca3af'
    plt.rcParams['xtick.color'] = '#9ca3af'
    plt.rcParams['ytick.color'] = '#9ca3af'
    plt.rcParams['font.family'] = 'sans-serif'

    conn = get_db_connection()
    
    # ----------------------------------------------------
    # Chart 1: Stock Movement (IN vs OUT Volumes)
    # ----------------------------------------------------
    movement_data = Inventory.get_daily_movement(days=15)
    chart_movement = None
    if movement_data:
        df_mv = pd.DataFrame(movement_data)
        
        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.plot(df_mv['tx_date'], df_mv['total_in'], marker='o', linewidth=2.5, color='#10b981', label='Stock In')
        ax.plot(df_mv['tx_date'], df_mv['total_out'], marker='s', linewidth=2.5, color='#f43f5e', label='Stock Out')
        
        apply_chart_style(ax, "15-Day Stock Movement Traffic")
        ax.set_xlabel("Date")
        ax.set_ylabel("Quantity")
        # Rotate dates slightly for neatness
        plt.xticks(rotation=30, ha='right')
        ax.legend(facecolor='#12131c', edgecolor=(1.0, 1.0, 1.0, 0.1), loc='upper left')
        
        chart_movement = fig_to_base64(fig)

    # ----------------------------------------------------
    # Chart 2: Category Breakdown (Pie / Donut)
    # ----------------------------------------------------
    query_cat = "SELECT category, SUM(quantity) as stock_qty, SUM(quantity * unit_price) as stock_val FROM products GROUP BY category;"
    cat_data = conn.execute(query_cat).fetchall()
    chart_category = None
    if cat_data:
        df_cat = pd.DataFrame([dict(r) for r in cat_data])
        
        fig, ax = plt.subplots(figsize=(6, 3.5))
        # Custom palette colors matching the dashboard
        colors = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899', '#3b82f6']
        
        # Donut Chart
        wedges, texts, autotexts = ax.pie(
            df_cat['stock_qty'], 
            labels=df_cat['category'], 
            autopct='%1.1f%%', 
            startangle=140, 
            colors=colors[:len(df_cat)],
            textprops={'color': '#f3f4f6'},
            wedgeprops=dict(width=0.4, edgecolor=(1.0, 1.0, 1.0, 0.1), linewidth=1.5) # Ring width
        )
        
        # Customize autotexts (inside slices)
        for autotext in autotexts:
            autotext.set_color('#ffffff')
            autotext.set_weight('bold')
            autotext.set_fontsize(8.5)
            
        ax.set_title("Stock Quantity Category Share", color='#f3f4f6', fontsize=14, pad=15, fontweight='bold')
        chart_category = fig_to_base64(fig)

    # ----------------------------------------------------
    # Chart 3: Warehouse Occupancy vs Capacity by Zone
    # ----------------------------------------------------
    zone_data = Warehouse.get_zone_utilization()
    chart_zone = None
    if zone_data:
        df_zone = pd.DataFrame(zone_data)
        
        fig, ax = plt.subplots(figsize=(7, 3.5))
        x_indices = np.arange(len(df_zone['zone']))
        width = 0.35
        
        ax.bar(x_indices - width/2, df_zone['total_occupancy'], width, label='Current Occupancy', color='#06b6d4', edgecolor='none')
        ax.bar(x_indices + width/2, df_zone['total_capacity'], width, label='Total Capacity', color=(1.0, 1.0, 1.0, 0.08), edgecolor=(1.0, 1.0, 1.0, 0.2), linewidth=1)
        
        apply_chart_style(ax, "Warehouse Zone Load & Limits")
        ax.set_ylabel("Quantity Units")
        ax.set_xticks(x_indices)
        ax.set_xticklabels(df_zone['zone'])
        ax.legend(facecolor='#12131c', edgecolor=(1.0, 1.0, 1.0, 0.1))
        
        chart_zone = fig_to_base64(fig)

    # ----------------------------------------------------
    # Chart 4: Fast Moving Products (Top 5)
    # ----------------------------------------------------
    fast_moving = Inventory.get_fast_moving_products(limit=5)
    chart_fast = None
    if fast_moving:
        df_fast = pd.DataFrame(fast_moving)
        
        fig, ax = plt.subplots(figsize=(6, 3.5))
        # Horizontal bars
        bars = ax.barh(df_fast['product_name'], df_fast['total_sold'], color='#8b5cf6', edgecolor='none')
        
        apply_chart_style(ax, "Top 5 Fast-Moving Items")
        ax.set_xlabel("Units Shipped (OUT)")
        
        # Add labels to the ends of the bars
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                    va='center', ha='left', color='#f3f4f6', fontweight='bold', fontsize=9)
            
        chart_fast = fig_to_base64(fig)

    conn.close()

    # Get supplementary tables for details listing
    slow_moving = Inventory.get_slow_moving_products(limit=5)
    
    return render_template(
        'analytics.html',
        active_page='analytics',
        chart_movement=chart_movement,
        chart_category=chart_category,
        chart_zone=chart_zone,
        chart_fast=chart_fast,
        slow_moving=slow_moving
    )
