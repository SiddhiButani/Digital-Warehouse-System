import sqlite3
from database.db import get_db_connection
from utils.qr_generator import generate_product_qr

class Product:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        query = """
            SELECT p.*, s.company_name AS supplier_name, sh.zone AS shelf_zone
            FROM products p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            LEFT JOIN warehouse_shelves sh ON p.shelf_id = sh.shelf_id;
        """
        rows = conn.execute(query).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(product_id):
        conn = get_db_connection()
        query = """
            SELECT p.*, s.company_name AS supplier_name, sh.zone AS shelf_zone
            FROM products p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            LEFT JOIN warehouse_shelves sh ON p.shelf_id = sh.shelf_id
            WHERE p.id = ?;
        """
        row = conn.execute(query, (product_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create_product(product_id, name, category, qty, price, shelf_id, supplier_id, user_id=1):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if shelf is overcapacity
            if shelf_id:
                shelf = cursor.execute("SELECT capacity, occupancy FROM warehouse_shelves WHERE shelf_id = ?;", (shelf_id,)).fetchone()
                if shelf:
                    if shelf['occupancy'] + qty > shelf['capacity']:
                        return False, "Selected shelf does not have enough capacity."

            # Generate QR Code
            qr_path = generate_product_qr(product_id)

            # Insert product
            cursor.execute(
                """INSERT INTO products (id, product_name, category, quantity, unit_price, qr_code_path, shelf_id, supplier_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
                (product_id, name, category, qty, price, qr_path, shelf_id, supplier_id)
            )

            # Update occupancy
            if shelf_id:
                cursor.execute(
                    "UPDATE warehouse_shelves SET occupancy = occupancy + ? WHERE shelf_id = ?;",
                    (qty, shelf_id)
                )

            # Insert initial transaction log (IN)
            cursor.execute(
                """INSERT INTO inventory_transactions (product_id, transaction_type, quantity, user_id)
                   VALUES (?, 'IN', ?, ?);""",
                (product_id, qty, user_id or 1)
            )

            conn.commit()
            return True, "Product created successfully."
        except sqlite3.IntegrityError:
            return False, f"Product ID {product_id} already exists."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def update_product(product_id, name, category, price, shelf_id, supplier_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Get old product info to compare shelf change
            old_prod = cursor.execute("SELECT quantity, shelf_id FROM products WHERE id = ?;", (product_id,)).fetchone()
            if not old_prod:
                return False, "Product not found."

            old_shelf = old_prod['shelf_id']
            qty = old_prod['quantity']

            if old_shelf != shelf_id:
                # Deduct from old shelf
                if old_shelf:
                    cursor.execute(
                        "UPDATE warehouse_shelves SET occupancy = MAX(0, occupancy - ?) WHERE shelf_id = ?;",
                        (qty, old_shelf)
                    )
                # Check and add to new shelf
                if shelf_id:
                    shelf = cursor.execute("SELECT capacity, occupancy FROM warehouse_shelves WHERE shelf_id = ?;", (shelf_id,)).fetchone()
                    if shelf:
                        if shelf['occupancy'] + qty > shelf['capacity']:
                            conn.rollback()
                            return False, "New shelf does not have enough capacity."
                        cursor.execute(
                            "UPDATE warehouse_shelves SET occupancy = occupancy + ? WHERE shelf_id = ?;",
                            (qty, shelf_id)
                        )

            # Update product details
            cursor.execute(
                """UPDATE products 
                   SET product_name = ?, category = ?, unit_price = ?, shelf_id = ?, supplier_id = ?
                   WHERE id = ?;""",
                (name, category, price, shelf_id, supplier_id, product_id)
            )

            conn.commit()
            return True, "Product updated successfully."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def delete_product(product_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            prod = cursor.execute("SELECT quantity, shelf_id FROM products WHERE id = ?;", (product_id,)).fetchone()
            if not prod:
                return False, "Product not found."

            qty = prod['quantity']
            shelf_id = prod['shelf_id']

            # Update shelf occupancy
            if shelf_id:
                cursor.execute(
                    "UPDATE warehouse_shelves SET occupancy = MAX(0, occupancy - ?) WHERE shelf_id = ?;",
                    (qty, shelf_id)
                )

            # Delete product
            cursor.execute("DELETE FROM products WHERE id = ?;", (product_id,))
            conn.commit()
            return True, "Product deleted successfully."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def adjust_stock(product_id, tx_type, qty, user_id):
        """
        Adjust stock quantity and records the inventory transaction.
        tx_type can be: 'IN', 'OUT', or 'ADJUST'
        For 'IN': increases stock.
        For 'OUT': decreases stock.
        For 'ADJUST': quantity is the new absolute quantity.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            prod = cursor.execute("SELECT quantity, shelf_id FROM products WHERE id = ?;", (product_id,)).fetchone()
            if not prod:
                return False, "Product not found."

            current_qty = prod['quantity']
            shelf_id = prod['shelf_id']
            diff = 0

            if tx_type == 'IN':
                diff = qty
            elif tx_type == 'OUT':
                if current_qty < qty:
                    return False, "Insufficient stock quantity available."
                diff = -qty
            elif tx_type == 'ADJUST':
                diff = qty - current_qty

            if diff == 0:
                return True, "No stock adjustment needed."

            # If increasing stock, check shelf capacity
            if diff > 0 and shelf_id:
                shelf = cursor.execute("SELECT capacity, occupancy FROM warehouse_shelves WHERE shelf_id = ?;", (shelf_id,)).fetchone()
                if shelf:
                    if shelf['occupancy'] + diff > shelf['capacity']:
                        return False, "Operation exceeds warehouse shelf capacity."

            # Update product quantity
            cursor.execute(
                "UPDATE products SET quantity = quantity + ? WHERE id = ?;",
                (diff, product_id)
            )

            # Update shelf occupancy
            if shelf_id:
                cursor.execute(
                    "UPDATE warehouse_shelves SET occupancy = MAX(0, occupancy + ?) WHERE shelf_id = ?;",
                    (diff, shelf_id)
                )

            # Log transaction
            # In SQLite transaction log, quantity is stored as the amount changed (usually positive for flow context, with transaction_type indicating direction)
            # We store the absolute change value in transaction log
            cursor.execute(
                """INSERT INTO inventory_transactions (product_id, transaction_type, quantity, user_id)
                   VALUES (?, ?, ?, ?);""",
                (product_id, tx_type, abs(diff), user_id)
            )

            conn.commit()
            return True, "Stock adjusted successfully."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def get_low_stock(threshold=10):
        conn = get_db_connection()
        query = """
            SELECT p.*, sh.zone AS shelf_zone
            FROM products p
            LEFT JOIN warehouse_shelves sh ON p.shelf_id = sh.shelf_id
            WHERE p.quantity <= ?;
        """
        rows = conn.execute(query, (threshold,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_summary_stats():
        conn = get_db_connection()
        stats = {}
        # Total unique products
        stats['total_products'] = conn.execute("SELECT COUNT(*) FROM products;").fetchone()[0]
        # Total physical stock sum
        stats['total_stock'] = conn.execute("SELECT SUM(quantity) FROM products;").fetchone()[0] or 0
        # Total value of warehouse inventory
        stats['total_value'] = conn.execute("SELECT SUM(quantity * unit_price) FROM products;").fetchone()[0] or 0.0
        # Total low stock count (using threshold 10)
        stats['low_stock_count'] = conn.execute("SELECT COUNT(*) FROM products WHERE quantity <= 10;").fetchone()[0]
        conn.close()
        return stats
