from database.db import get_db_connection

class Inventory:
    @staticmethod
    def get_transactions(limit=100):
        conn = get_db_connection()
        query = """
            SELECT t.id, t.product_id, p.product_name, t.transaction_type, t.quantity, t.date, u.username
            FROM inventory_transactions t
            JOIN products p ON t.product_id = p.id
            JOIN users u ON t.user_id = u.id
            ORDER BY t.date DESC
            LIMIT ?;
        """
        rows = conn.execute(query, (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_transactions_by_product(product_id):
        conn = get_db_connection()
        query = """
            SELECT t.id, t.transaction_type, t.quantity, t.date, u.username
            FROM inventory_transactions t
            JOIN users u ON t.user_id = u.id
            WHERE t.product_id = ?
            ORDER BY t.date DESC;
        """
        rows = conn.execute(query, (product_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_daily_movement(days=7):
        """
        Returns stock changes (IN sum vs OUT sum) grouped by date.
        """
        conn = get_db_connection()
        query = """
            SELECT date(date) AS tx_date,
                   SUM(CASE WHEN transaction_type = 'IN' THEN quantity ELSE 0 END) AS total_in,
                   SUM(CASE WHEN transaction_type = 'OUT' THEN quantity ELSE 0 END) AS total_out
            FROM inventory_transactions
            WHERE date >= datetime('now', ?)
            GROUP BY tx_date
            ORDER BY tx_date ASC;
        """
        expr = f"-{days} days"
        rows = conn.execute(query, (expr,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_fast_moving_products(limit=5):
        """
        Returns products with the highest sum of 'OUT' quantities.
        """
        conn = get_db_connection()
        query = """
            SELECT p.id, p.product_name, SUM(t.quantity) AS total_sold
            FROM inventory_transactions t
            JOIN products p ON t.product_id = p.id
            WHERE t.transaction_type = 'OUT'
            GROUP BY p.id
            ORDER BY total_sold DESC
            LIMIT ?;
        """
        rows = conn.execute(query, (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_slow_moving_products(limit=5):
        """
        Returns products with minimal or no stock movement ('OUT' transactions),
        ordered by total quantity currently sitting in stock.
        """
        conn = get_db_connection()
        query = """
            SELECT p.id, p.product_name, p.quantity, COALESCE(SUM(CASE WHEN t.transaction_type = 'OUT' THEN t.quantity ELSE 0 END), 0) AS total_sold
            FROM products p
            LEFT JOIN inventory_transactions t ON p.id = t.product_id
            GROUP BY p.id
            ORDER BY total_sold ASC, p.quantity DESC
            LIMIT ?;
        """
        rows = conn.execute(query, (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]
