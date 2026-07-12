from database.db import get_db_connection

class Supplier:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM suppliers ORDER BY company_name ASC;").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(supplier_id):
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM suppliers WHERE id = ?;", (supplier_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(company_name, contact_person, phone, email, address):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO suppliers (company_name, contact_person, phone, email, address)
                   VALUES (?, ?, ?, ?, ?);""",
                (company_name, contact_person, phone, email, address)
            )
            conn.commit()
            return True, "Supplier added successfully.", cursor.lastrowid
        except Exception as e:
            conn.rollback()
            return False, str(e), None
        finally:
            conn.close()

    @staticmethod
    def update(supplier_id, company_name, contact_person, phone, email, address):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """UPDATE suppliers 
                   SET company_name = ?, contact_person = ?, phone = ?, email = ?, address = ?
                   WHERE id = ?;""",
                (company_name, contact_person, phone, email, address, supplier_id)
            )
            conn.commit()
            return True, "Supplier updated successfully."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def delete(supplier_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if products are tied to this supplier
            linked_products = cursor.execute("SELECT COUNT(*) FROM products WHERE supplier_id = ?;", (supplier_id,)).fetchone()[0]
            if linked_products > 0:
                # Set supplier_id to NULL for these products, or reject deletion.
                # Let's set supplier_id to NULL (ON DELETE SET NULL is active in DB, but we do it gracefully or alert)
                cursor.execute("UPDATE products SET supplier_id = NULL WHERE supplier_id = ?;", (supplier_id,))
            
            cursor.execute("DELETE FROM suppliers WHERE id = ?;", (supplier_id,))
            conn.commit()
            return True, "Supplier deleted successfully."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def get_summary_stats():
        conn = get_db_connection()
        stats = {}
        # Total suppliers count
        stats['total_suppliers'] = conn.execute("SELECT COUNT(*) FROM suppliers;").fetchone()[0]
        
        # Suppliers performance details (number of products supplied and total value supplied)
        query = """
            SELECT s.id, s.company_name, s.contact_person, COUNT(p.id) AS product_count, SUM(p.quantity * p.unit_price) AS total_value
            FROM suppliers s
            LEFT JOIN products p ON s.id = p.supplier_id
            GROUP BY s.id;
        """
        rows = conn.execute(query).fetchall()
        stats['performance'] = [dict(r) for r in rows]
        conn.close()
        return stats
