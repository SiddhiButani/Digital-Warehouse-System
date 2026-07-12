import sqlite3
import os
import sys
from werkzeug.security import generate_password_hash

# Add root directory to path to allow imports from utils/config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config
from utils.qr_generator import generate_product_qr

def get_db_connection():
    """
    Establishes a connection to the SQLite database and returns the connection object.
    Enforces foreign keys.
    """
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """
    Initializes the database using the schema.sql file and seeds initial data.
    """
    Config.init_app()
    db_path = Config.DB_PATH
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

    print(f"Initializing database at: {db_path}")

    # Read schema
    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Execute schema
    cursor.executescript(schema_sql)
    conn.commit()

    print("Schema executed successfully. Seeding initial data...")

    # 1. Seed Users (Hashed Passwords)
    users = [
        ('admin', generate_password_hash('admin123'), 'Admin'),
        ('manager', generate_password_hash('manager123'), 'Manager'),
        ('staff', generate_password_hash('staff123'), 'Staff')
    ]
    cursor.executemany(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?);",
        users
    )
    conn.commit()

    # 2. Seed Suppliers
    suppliers = [
        ('Global Tech Distributors', 'John Doe', '555-0199', 'john@globaltech.com', '123 Tech Way, Silicon Valley, CA'),
        ('Apex Supplies Inc.', 'Sarah Smith', '555-0233', 'sarah@apex.com', '456 Warehouse Rd, Industrial Area, TX'),
        ('Pioneer Food & Beverage', 'Michael Brown', '555-0455', 'michael@pioneer.com', '789 Grocery Blvd, Chicago, IL')
    ]
    cursor.executemany(
        "INSERT INTO suppliers (company_name, contact_person, phone, email, address) VALUES (?, ?, ?, ?, ?);",
        suppliers
    )
    conn.commit()

    # 3. Seed Shelves
    # Let's seed Zone A (capacity 100), Zone B (capacity 150), Zone C (capacity 200)
    shelves = [
        ('A-01', 'Zone A', 100, 0),
        ('A-02', 'Zone A', 100, 0),
        ('A-03', 'Zone A', 100, 0),
        ('A-04', 'Zone A', 100, 0),
        ('B-01', 'Zone B', 150, 0),
        ('B-02', 'Zone B', 150, 0),
        ('B-03', 'Zone B', 150, 0),
        ('B-04', 'Zone B', 150, 0),
        ('C-01', 'Zone C', 200, 0),
        ('C-02', 'Zone C', 200, 0)
    ]
    cursor.executemany(
        "INSERT INTO warehouse_shelves (shelf_id, zone, capacity, occupancy) VALUES (?, ?, ?, ?);",
        shelves
    )
    conn.commit()

    # 4. Seed Products and generate QR codes
    products_to_seed = [
        ('PROD-1001', 'Wireless Mouse', 'Electronics', 50, 25.00, 'A-01', 1),
        ('PROD-1002', 'Mechanical Keyboard', 'Electronics', 30, 80.00, 'A-02', 1),
        ('PROD-1003', 'Ergonomic Chair', 'Office Furniture', 15, 150.00, 'B-01', 2),
        ('PROD-1004', 'Standing Desk', 'Office Furniture', 10, 350.00, 'B-02', 2),
        ('PROD-1005', 'Organic Almonds', 'Food & Beverage', 120, 12.00, 'C-01', 3)
    ]
    
    # We need unit_price to be float
    # We format properly
    for item in products_to_seed:
        p_id, p_name, cat, qty, price, shelf, sup_id = item
        # Generate QR code
        qr_path = generate_product_qr(p_id)
        
        # Insert product
        cursor.execute(
            """INSERT INTO products (id, product_name, category, quantity, unit_price, qr_code_path, shelf_id, supplier_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
            (p_id, p_name, cat, qty, float(price), qr_path, shelf, sup_id)
        )
        
        # Update occupancy on the shelf
        cursor.execute(
            "UPDATE warehouse_shelves SET occupancy = occupancy + ? WHERE shelf_id = ?;",
            (qty, shelf)
        )

        # Log initial Transaction (STOCK IN)
        cursor.execute(
            """INSERT INTO inventory_transactions (product_id, transaction_type, quantity, date, user_id)
               VALUES (?, 'IN', ?, datetime('now', '-2 days'), 1);""",
            (p_id, qty)
        )
    
    conn.commit()

    # Let's seed a few mock transactions for analytical trends
    # Mocking some transactions over the last 2 days
    mock_transactions = [
        ('PROD-1001', 'OUT', 5, "datetime('now', '-1 days')", 1),
        ('PROD-1002', 'OUT', 2, "datetime('now', '-1 days')", 1),
        ('PROD-1005', 'OUT', 20, "datetime('now', '-1 days')", 1),
        ('PROD-1001', 'IN', 10, "datetime('now')", 1),
        ('PROD-1003', 'OUT', 3, "datetime('now')", 1),
        ('PROD-1004', 'OUT', 1, "datetime('now')", 1),
    ]

    for tx in mock_transactions:
        p_id, tx_type, qty, date_expr, user_id = tx
        # We need to execute using SQL raw timestamp expression
        cursor.execute(
            f"""INSERT INTO inventory_transactions (product_id, transaction_type, quantity, date, user_id)
               VALUES (?, ?, ?, {date_expr}, ?);""",
            (p_id, tx_type, qty, user_id)
        )
        
        # Adjust quantities & occupancy accordingly
        mod = 1 if tx_type == 'IN' else -1
        cursor.execute(
            "UPDATE products SET quantity = quantity + ? WHERE id = ?;",
            (qty * mod, p_id)
        )
        cursor.execute(
            "UPDATE warehouse_shelves SET occupancy = occupancy + ? WHERE shelf_id = (SELECT shelf_id FROM products WHERE id = ?);",
            (qty * mod, p_id)
        )

    conn.commit()
    conn.close()
    print("Database initialization and seeding completed successfully!")

if __name__ == '__main__':
    init_db()
