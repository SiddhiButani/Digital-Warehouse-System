# Digital Warehouse Management System (DWMS)

A lightweight, developer-focused warehouse inventory management system built with Python, Flask, SQLite, and OpenCV. DWMS provides real-time stock ledger tracking, shelf capacity management, automated QR code label generation, web and desktop QR scanning, analytics, and multi-format report exports (Excel, PDF, CSV).

---

## Features

### 1. Master Product Catalog & QR Labeling
- Master product directory tracking SKU codes, item descriptions, categories, unit prices, and stock counts.
- Automated generation of QR code sticker assets upon product registration.
- Print-ready QR code label generation directly from product master records.
- Bin and shelf assignment linked to warehouse zones.

### 2. Stock Movement Ledger & Adjustments
- Real-time transaction ledger tracking every stock operation (`IN`, `OUT`, `ADJUST`).
- Operator attribution: movements are stamped with the username of the authenticated operator.
- Dynamic shelf occupancy recalculation on every stock movement.
- Low-stock threshold alerts (highlighted in red when quantity $\le$ 10).

### 3. QR Code Scanning (Web & Desktop)
- **Webcam Browser Scanner:** Integrated WebRTC camera interface that captures frames and decodes QR codes via backend OpenCV processing. Automatically loads SKU details into a quick-adjustment workstation.
- **Desktop Scan Station (`scanner_desktop.py`):** Dedicated desktop terminal using OpenCV with live webcam feed, viewfinder bounding box, and interactive CLI prompts for high-speed barcode/QR intake and dispatch.

### 4. Warehouse Shelf & Zone Management
- Zone-level storage tracking (Zone A, Zone B, Zone C) with individual shelf capacity and real-time occupancy.
- Visual capacity indicators warning when shelf capacity limits are approached or exceeded.

### 5. Supplier Directory
- Vendor contact registry including company names, contact persons, phone numbers, email addresses, and warehouse locations.
- Live valuation metrics displaying the total SKU count and dollar value of inventory supplied by each partner.

### 6. Analytics & Dead-Stock Audit
- **Stock Movement Traffic:** 15-day time-series line chart tracking Stock IN vs. Stock OUT volume.
- **Category Share:** Donut chart breakdown of warehouse inventory valuation and item distribution.
- **Zone Load & Limits:** Comparative bar chart showing current occupancy against total capacity limits.
- **High-Velocity SKUs:** Horizontal bar ranking of fast-moving products.
- **Dead-Stock Audit:** Filtered table identifying slow-moving products occupying shelf capacity with minimal turnover.

### 7. Multi-Format Report Center
- Generate and download complete snapshot audits in three formats:
  - **Excel (`.xlsx`):** Styled workbooks via `openpyxl`.
  - **PDF (`.pdf`):** Formatted tabular audit documents via `reportlab`.
  - **CSV (`.csv`):** Standard delimited files for database migration and spreadsheet analysis.
- Reports available: Inventory Balance, Transaction Audit Trail, and Supplier Registry.

### 8. Role-Based Access Control (RBAC)
- Session-based authentication with Werkzeug password hashing.
- Three user roles:
  - **Admin:** Full access (product management, supplier management, inventory overrides, reports, analytics).
  - **Manager:** Catalog editing, supplier management, stock reconciliation, and reporting.
  - **Staff:** Day-to-day operations (stock IN/OUT logging, QR scanning, product directory lookup).

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.10+, Flask, Werkzeug |
| **Database** | SQLite3 (foreign key integrity enforced) |
| **Computer Vision** | OpenCV (`opencv-python`), `qrcode[pil]` |
| **Data & Visuals** | Pandas, NumPy, Matplotlib |
| **Document Export** | OpenPyXL (Excel), ReportLab (PDF), standard CSV |
| **UI & Styling** | Vanilla HTML5 / CSS3, system font stack, flat 1px borders, 960px container |

---

## Project Structure

```text
Digital-Warehouse-System/
├── app.py                  # Flask application factory and entry point
├── config.py               # Application settings, paths, and thresholds
├── requirements.txt        # Python dependency manifest
├── scanner_desktop.py      # Standalone OpenCV desktop webcam scanner
├── verify_system.py        # Automated system diagnostics and verification
├── database/
│   ├── db.py               # Database connection factory and seed routine
│   ├── schema.sql          # SQLite schema definition
│   └── warehouse.db        # SQLite database file
├── models/
│   ├── inventory.py        # Stock movement and analytics query methods
│   ├── product.py          # Product CRUD and stock adjustment logic
│   ├── supplier.py         # Vendor partner model methods
│   ├── user.py             # User lookup and authentication
│   └── warehouse.py        # Shelf and zone occupancy calculations
├── routes/
│   ├── analytics.py        # Chart generation and performance metrics
│   ├── auth.py             # Login, logout, and session decorators
│   ├── dashboard.py        # Main KPI dashboard
│   ├── inventory.py        # Ledger, manual adjustments, and web scanner API
│   ├── products.py         # Product master records and QR views
│   ├── reports.py          # Excel, PDF, and CSV download endpoints
│   └── supplier.py         # Supplier directory management
├── static/
│   ├── css/
│   │   └── style.css       # Clean, human-designed developer UI styles
│   ├── qrcodes/            # Generated QR code image files (.png)
│   └── uploads/            # Uploaded asset storage
├── templates/              # Jinja2 HTML templates
│   ├── analytics.html
│   ├── base.html
│   ├── dashboard.html
│   ├── inventory.html
│   ├── login.html
│   ├── product_detail.html
│   ├── products.html
│   ├── reports.html
│   ├── scanner.html
│   └── suppliers.html
└── utils/
    └── qr_generator.py     # QR code image generation utility
```

---

## Getting Started

### Prerequisites

- **Python 3.10 or higher** installed on your system.
- A functional **webcam** (required for QR code scanner features).

### 1. Clone or Open the Repository

```bash
git clone https://github.com/your-username/Digital-Warehouse-System.git
cd Digital-Warehouse-System
```

### 2. Set Up a Virtual Environment

**On Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify System Environment

Run the built-in diagnostic test to confirm SQLite, Matplotlib, ReportLab, and OpenPyXL are functioning properly:

```bash
python verify_system.py
```

### 5. Start the Web Application

```bash
python app.py
```

The database initializes and seeds automatically on first launch if `warehouse.db` does not exist.

Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## Default User Accounts

The database comes pre-seeded with three default accounts for testing:

| Username | Password | Role | Permissions |
|---|---|---|---|
| `admin` | `admin123` | **Admin** | Full system access: add/edit/delete products and suppliers, reconcile inventory overrides, export reports |
| `manager` | `manager123` | **Manager** | Catalog management, stock adjustments, vendor management, report exports |
| `staff` | `staff123` | **Staff** | Daily stock movements (`IN` / `OUT`), webcam QR scanning, catalog search |

---

## Running the Desktop Scanner

For dedicated scanning workstations without a web browser, launch the OpenCV terminal scan station:

```bash
python scanner_desktop.py
```

1. Hold a printed or screen-displayed QR code in front of the camera.
2. The scanner will identify the SKU and display product details and current bin location.
3. In the terminal prompt, enter `I` for Stock IN, `O` for Stock OUT, and specify the quantity.
4. Press `q` or `ESC` in the camera window to exit.

---

## Configuration

Settings can be customized in [`config.py`](file:///e:/Digital-Warehouse-System/config.py) or via environment variables:

- `SECRET_KEY`: Flask session encryption key.
- `LOW_STOCK_THRESHOLD`: Count at which items are flagged as low stock (default: `10`).
- `DB_PATH`: Path to the SQLite database file.
- `QRCODE_FOLDER`: Directory where generated QR image files are saved.

---

## License

This project is licensed under the MIT License.
