from database.db import get_db_connection

class Warehouse:
    @staticmethod
    def get_all_shelves():
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM warehouse_shelves ORDER BY shelf_id ASC;").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_shelf(shelf_id):
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM warehouse_shelves WHERE shelf_id = ?;", (shelf_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create_shelf(shelf_id, zone, capacity):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO warehouse_shelves (shelf_id, zone, capacity, occupancy)
                   VALUES (?, ?, ?, 0);""",
                (shelf_id, zone, capacity)
            )
            conn.commit()
            return True, "Warehouse shelf created successfully."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def update_shelf(shelf_id, zone, capacity):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Verify capacity is not smaller than current occupancy
            shelf = cursor.execute("SELECT occupancy FROM warehouse_shelves WHERE shelf_id = ?;", (shelf_id,)).fetchone()
            if shelf and capacity < shelf['occupancy']:
                return False, f"Capacity cannot be reduced below current occupancy ({shelf['occupancy']})."

            cursor.execute(
                """UPDATE warehouse_shelves 
                   SET zone = ?, capacity = ?
                   WHERE shelf_id = ?;""",
                (zone, capacity, shelf_id)
            )
            conn.commit()
            return True, "Warehouse shelf updated successfully."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def delete_shelf(shelf_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Verify occupancy is 0 and no products are assigned
            shelf = cursor.execute("SELECT occupancy FROM warehouse_shelves WHERE shelf_id = ?;", (shelf_id,)).fetchone()
            if not shelf:
                return False, "Shelf not found."
            if shelf['occupancy'] > 0:
                return False, "Cannot delete a shelf that currently holds items."

            cursor.execute("DELETE FROM warehouse_shelves WHERE shelf_id = ?;", (shelf_id,))
            conn.commit()
            return True, "Warehouse shelf deleted successfully."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def get_zone_utilization():
        """
        Calculates occupancy and capacity grouped by warehouse zones.
        """
        conn = get_db_connection()
        query = """
            SELECT zone, SUM(occupancy) AS total_occupancy, SUM(capacity) AS total_capacity
            FROM warehouse_shelves
            GROUP BY zone;
        """
        rows = conn.execute(query).fetchall()
        conn.close()
        
        result = []
        for r in rows:
            d = dict(r)
            cap = d['total_capacity'] or 1
            d['utilization_percentage'] = round((d['total_occupancy'] / cap) * 100, 2)
            result.append(d)
        return result
