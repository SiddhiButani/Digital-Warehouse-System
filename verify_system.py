import os
import sys

# Append root path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

print("Running Digital Warehouse Verification Checks...")

try:
    print("\n1. Testing Database connection and models...")
    from database.db import get_db_connection
    conn = get_db_connection()
    res = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    tables = [r[0] for r in res]
    print(f"   Database tables verified: {tables}")
    conn.close()
    
    # Test User Model
    from models.user import User
    users = User.get_all()
    print(f"   Registered Users: {[u.username for u in users]} (Count: {len(users)})")
    
    # Test Product Model
    from models.product import Product
    prods = Product.get_all()
    print(f"   Warehouse Products SKU: {[p['id'] for p in prods]} (Count: {len(prods)})")
except Exception as e:
    print(f"[FAIL] Database / Model Check Failed: {e}")
    sys.exit(1)

try:
    print("\n2. Testing Matplotlib & Pandas compilation...")
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    # Sample plot
    df = pd.DataFrame({'days': [1, 2, 3], 'qty': [10, 20, 15]})
    fig, ax = plt.subplots(figsize=(4, 2))
    ax.plot(df['days'], df['qty'])
    plt.close(fig)
    print("   Matplotlib Agg backend rendering is operational.")
except Exception as e:
    print(f"[FAIL] Data Analysis plotting check failed: {e}")
    sys.exit(1)

try:
    print("\n3. Testing PDF (ReportLab) compiler...")
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    import io
    
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [Paragraph("System Verification PDF Document", styles['Normal'])]
    doc.build(elements)
    print("   ReportLab PDF compilation is operational.")
except Exception as e:
    print(f"[FAIL] PDF compiler engine check failed: {e}")
    sys.exit(1)

try:
    print("\n4. Testing Excel (OpenPyXL) exporter...")
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Verification"
    ws.append(["Col1", "Col2"])
    ws.append([100, 200])
    buf = io.BytesIO()
    wb.save(buf)
    print("   OpenPyXL Excel creation is operational.")
except Exception as e:
    print(f"[FAIL] Excel exporter engine check failed: {e}")
    sys.exit(1)

print("\n==============================================")
print("  ALL CORE SYSTEM SUB-COMPONENTS VERIFIED OK!  ")
print("==============================================")
