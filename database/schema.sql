-- SQL Schema for Digital Warehouse Management System

-- Drop tables if they exist
DROP TABLE IF EXISTS inventory_transactions;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS warehouse_shelves;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS users;

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

-- Inventory Transactions Table
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
