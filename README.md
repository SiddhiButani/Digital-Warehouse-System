# 📦 Digital Warehouse Management System (DWMS)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-green.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://www.sqlite.org/)
[![Computer Vision](https://img.shields.io/badge/Vision-OpenCV-red.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade, full-stack **Digital Warehouse Management System (DWMS)** built with Python and Flask. The platform streamlines inventory tracking, stock adjustments, supplier relationships, shelf location allocation, automated QR code generation, real-time desktop webcam QR scanning, visual analytics, and multi-format reporting (PDF, Excel, CSV).

---

## 📋 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Directory Structure](#-directory-structure)
- [Database Schema](#-database-schema)
- [Installation & Setup](#-installation--setup)
- [Default Login Credentials](#-default-login-credentials)
- [Application Modules](#-application-modules)
  - [1. Web Dashboard & Inventory Management](#1-web-dashboard--inventory-management)
  - [2. Desktop OpenCV Camera Scan Station](#2-desktop-opencv-camera-scan-station)
  - [3. Dynamic Analytics Engine](#3-dynamic-analytics-engine)
  - [4. Multi-Format Report Exporter](#4-multi-format-report-exporter)
  - [5. System Verification Suite](#5-system-verification-suite)
- [API & Route Summary](#-api--route-summary)
- [License](#-license)

---

## ✨ Key Features

- **🔐 Role-Based Access Control (RBAC):** Tiered permissions for `Admin`, `Manager`, and `Staff` roles with password hashing (`werkzeug.security`).
- **🏷️ Product & SKU Management:** Full CRUD capabilities for products, complete with auto-calculated total valuation, category assignment, shelf location linking, supplier mapping, and low-stock alerts.
- **📱 Automated QR Code Engine:** Dynamically generates high-resolution QR codes for every SKU upon product registration and updates stock status automatically.
- **📷 Desktop OpenCV Camera Scan Station:** Dedicated desktop camera barcode/QR scanner (`scanner_desktop.py`) with bounding-box visual overlays, live SKU lookup, and terminal-guided Stock IN/OUT processing.
- **🏗️ Warehouse Shelf & Zone Tracking:** Monitor shelf occupancy rates, zone capacities (`Zone A`, `Zone B`, `Zone C`), and physical shelf location mapping (`A-01`, `B-02`, etc.).
- **🤝 Supplier Directory Management:** Track manufacturer and vendor contact persons, phone numbers, email addresses, and warehouse locations.
- **📊 Interactive Data Analytics:** Real-time data visualization built with `Pandas` and `Matplotlib` (Agg backend), featuring stock valuation breakdown, shelf utilization density, and stock movement velocity.
- **📄 Multi-Format Export Engine:** One-click report generation in PDF format (`ReportLab`), Excel spreadsheets (`OpenPyXL`), and standard CSV files.
- **🧪 System Health Verification:** Built-in automated diagnostic script (`verify_system.py`) to test database connections, graphics compilers, PDF engines, and Excel generators.

---

## 🏛️ System Architecture

```
                                +-----------------------------------+
                                |     Desktop Workstation Camera    |
                                |       (scanner_desktop.py)        |
                                +-----------------+-----------------+
                                                  |
                                                  v  OpenCV / SQLite
+-------------------+           +-----------------+-----------------+
|   Web Browser     | <-------> |    Flask Web Application Server   |
| (Jinja2 Templates)|   HTTP    |             (app.py)              |
+-------------------+           +-----------------+-----------------+
                                                  |
                  +-------------------------------+-------------------------------+
                  |                               |                               |
                  v                               v                               v
       +--------------------+          +--------------------+          +--------------------+
       |  Data Models & DB  |          | Analytics & Plots  |          | Report Exporters   |
       |  (SQLite / models) |          | (Pandas/Matplotlib)|          |(ReportLab/OpenPyXL)|
       +--------------------+          +--------------------+          +--------------------+
```

---

## 💻 Technology Stack

| Category | Technology / Library | Description |
| :--- | :--- | :--- |
| **Backend** | Python 3.8+, Flask | Web server framework with modular Blueprints |
| **Database** | SQLite 3 | Embedded relational database with Foreign Keys enabled |
| **Computer Vision** | OpenCV (`opencv-python`) | Webcam stream parsing & QR code detection |
| **QR Generation** | `qrcode`, `Pillow (PIL)` | High-res PNG QR code generation |
| **Analytics & Data** | `pandas`, `numpy`, `matplotlib` | Data manipulation & server-side chart rendering |
| **Document Export** | `reportlab`, `openpyxl`, `csv` | PDF generation & Excel spreadsheet compiling |
| **Security** | Werkzeug Security | PBKDF2 password hashing & secure session storage |
| **Frontend** | HTML5, CSS3, JavaScript, Jinja2 | Responsive web user interface |

---

## 📁 Directory Structure

```
Digital-Warehouse-System/
├── app.py                   # Flask Application Entry Point & Blueprint Registration
├── config.py                # Core Application Configurations & Storage Paths
├── scanner_desktop.py       # OpenCV Desktop Camera QR Scan Workstation Station
├── verify_system.py         # Automated System Health Check & Test Suite
├── requirements.txt         # Python Package Dependency List
│
├── database/
│   ├── db.py                # DB Connection Handlers & Data Seeder
│   ├── schema.sql           # DDL Relational Database Schema Definition
│   └── warehouse.db         # SQLite Database File
│
├── models/                  # Data Access Object Models
│   ├── user.py              # User authentication & RBAC model
│   ├── product.py           # SKU, stock adjustment & lookup model
│   ├── inventory.py         # Stock transaction log model
│   ├── supplier.py          # Supplier partner directory model
│   └── warehouse.py         # Shelf capacity & occupancy tracking model
│
├── routes/                  # Flask Controllers (Blueprints)
│   ├── auth.py              # Authentication login/logout handler
│   ├── dashboard.py         # Executive overview KPI & metrics dashboard
│   ├── products.py          # Product management & QR code routes
│   ├── inventory.py         # Stock IN / Stock OUT forms & history
│   ├── supplier.py          # Vendor directory CRUD routes
│   ├── analytics.py         # Matplotlib chart rendering engine
│   └── reports.py           # Multi-format report download routes (PDF, Excel, CSV)
│
├── utils/
│   └── qr_generator.py      # QR code image generator utility
│
├── static/
│   ├── qrcodes/             # Generated product QR code image assets
│   ├── uploads/             # Static file storage
│   ├── css/                 # Frontend styling assets
│   └── js/                  # Client-side JavaScript
│
├── templates/               # Jinja2 HTML View Templates
│
└── reports/                 # Output directory for exported reports
    ├── pdf/                 # Compiled PDF reports
    └── excel/               # Generated XLSX spreadsheets
```

---

## 🗄️ Database Schema

```sql
-- Users Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Admin', 'Manager', 'Staff'))
);

-- Suppliers Table
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT UNIQUE NOT NULL,
    contact_person TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT NOT NULL
);

-- Warehouse Shelves Table
CREATE TABLE warehouse_shelves (
    shelf_id TEXT PRIMARY KEY,
    zone TEXT NOT NULL,
    capacity INTEGER NOT NULL DEFAULT 100,
    occupancy INTEGER NOT NULL DEFAULT 0
);

-- Products Table
CREATE TABLE products (
    id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
    unit_price REAL NOT NULL CHECK(unit_price >= 0.0),
    qr_code_path TEXT NOT NULL, 
    shelf_id TEXT,
    supplier_id INTEGER,
    FOREIGN KEY(shelf_id) REFERENCES warehouse_shelves(shelf_id) ON DELETE SET NULL,
    FOREIGN KEY(supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
);

-- Inventory Transactions Audit Table
CREATE TABLE inventory_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('IN', 'OUT', 'ADJUST')),
    quantity INTEGER NOT NULL,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

---

## 🚀 Installation & Setup

### Prerequisites

Ensure you have Python **3.8 or higher** installed on your system.

### 1. Clone the Repository
```bash
git clone https://github.com/SiddhiButani/Digital-Warehouse-System.git
cd Digital-Warehouse-System
```

### 2. Create and Activate a Virtual Environment
- **On Windows:**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
- **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database & Seed Data
*(Note: Running the app will automatically seed the database if `warehouse.db` is missing, but you can manually re-initialize anytime)*
```bash
python database/db.py
```

### 5. Run the Flask Web Application
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🔑 Default Login Credentials

The initial seed script populates default test users for testing Role-Based Access Control (RBAC):

| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Full control (User management, Products, Suppliers, Reports, Audits) |
| **Manager** | `manager` | `manager123` | Product management, Stock adjustments, Supplier access & Reports |
| **Staff** | `staff` | `staff123` | Read-only views & basic Stock IN / OUT operations |

---

## ⚙️ Application Modules

### 1. Web Dashboard & Inventory Management
- **Dashboard (`/`)**: Displays high-level KPIs including Total Stock Count, Total Valuation ($), Active Suppliers, Low-Stock Warnings, and recent audit logs.
- **Product Catalog (`/products`)**: Add, edit, or delete inventory items. Generating a product creates a custom QR code automatically.
- **Stock Movement (`/inventory`)**: Register Stock IN (receiving), Stock OUT (shipping), or manual quantity adjustments with logged timestamp and operator metadata.

### 2. Desktop OpenCV Camera Scan Station
For hands-free warehouse workstation scanning, run the desktop camera scanner tool:
```bash
python scanner_desktop.py
```
- **Live Bounding Box Overlay**: Target guide box visually assists camera alignment.
- **Instant SKU Decoding**: Automatically parses QR barcodes captured in camera feed.
- **Terminal Control Loop**: Prompted options to instantly perform Stock IN (`I`) or Stock OUT (`O`) operations directly against `warehouse.db`.

### 3. Dynamic Analytics Engine
Access `/analytics` for graphical intelligence generated live:
- **Inventory Value by Category**: Bar charts visualizing financial asset distribution.
- **Stock Density per Shelf Zone**: Multi-zone capacity vs occupancy analysis.
- **Transaction Velocity**: Historical trend line of incoming vs outgoing shipments.

### 4. Multi-Format Report Exporter
Generate and download warehouse audit reports directly from `/reports`:
- 📄 **PDF Format**: Cleanly formatted documents compiled via `ReportLab`.
- 📊 **Excel Spreadsheet**: Styled `.xlsx` files generated using `OpenPyXL`.
- 📁 **CSV Export**: Raw data export for integration with external ERP systems.

### 5. System Verification Suite
Run the automated validation script to verify engine functionality and database integrity:
```bash
python verify_system.py
```
*Validates SQLite table structures, Matplotlib Agg backend, ReportLab compiler, and OpenPyXL sheet exporter.*

---

## 🛣️ API & Route Summary

| Module | Route Endpoint | HTTP Method | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `/auth/login` | `GET`, `POST` | User login & session initiation |
| | `/auth/logout` | `GET` | Terminate session |
| **Dashboard**| `/` | `GET` | Executive overview dashboard |
| **Products** | `/products/` | `GET` | View product catalog |
| | `/products/add` | `GET`, `POST` | Add new product & generate QR code |
| | `/products/edit/<id>` | `GET`, `POST` | Edit existing product details |
| | `/products/delete/<id>`| `POST` | Remove product |
| **Inventory**| `/inventory/` | `GET` | View inventory transaction history |
| | `/inventory/adjust` | `POST` | Process Stock IN / OUT transaction |
| **Suppliers**| `/suppliers/` | `GET`, `POST` | Manage vendor directory |
| **Analytics**| `/analytics/` | `GET` | View analytical visual charts |
| **Reports**  | `/reports/` | `GET` | Report download menu |
| | `/reports/export/<type>/<format>` | `GET` | Download PDF, Excel, or CSV report |

---

## 📜 License

This project is open-source under the **MIT License**. Feel free to modify and distribute for educational or commercial warehouse operations.
