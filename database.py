"""SQLite connection, schema creation, and demo data for the support agent."""
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).with_name("ecommerce.db")


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    connection = get_connection()
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS Products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            rating REAL NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS Customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS Orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL,
            estimated_delivery TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES Products(product_id)
        );
        CREATE TABLE IF NOT EXISTS Returns (
            return_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL,
            request_date TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES Orders(order_id)
        );
        CREATE TABLE IF NOT EXISTS CustomerMemory (
            memory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            memory_key TEXT NOT NULL,
            memory_value TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(customer_id, memory_key),
            FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
        );
        """
    )
    if connection.execute("SELECT COUNT(*) FROM Products").fetchone()[0] == 0:
        connection.executemany(
            "INSERT INTO Products VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("P1001", "SoundArc Wireless Headphones", "Headphones", 2499, "Active noise cancellation, 40-hour battery, and soft memory-foam cushions.", 24, 4.7),
                ("P1002", "PulseBeat Sport Earbuds", "Headphones", 1899, "Sweat-resistant earbuds with a secure fit and low-latency gaming mode.", 0, 4.5),
                ("P1003", "TerraGrip All-Weather Runner", "Running Shoes", 2799, "Breathable wide-fit trail runners with high-traction rubber soles.", 12, 4.8),
                ("P1004", "CodeCraft 14 Laptop", "Laptops", 56990, "14-inch laptop with 16GB RAM, 512GB SSD, and a developer-friendly keyboard.", 7, 4.6),
                ("P1005", "GameForge Pro Laptop", "Laptops", 74990, "High-refresh display, dedicated graphics, and fast cooling for modern games.", 3, 4.8),
                ("P1006", "BreezeView 27 Monitor", "Monitors", 18999, "27-inch QHD monitor with eye-care mode and USB-C connectivity.", 9, 4.4),
            ],
        )
        connection.executemany("INSERT INTO Customers VALUES (?, ?, ?)", [("CUST001", "Jordan Mitchell", "jordan@example.com"), ("CUST002", "Avery Lee", "avery@example.com")])
        connection.executemany(
            "INSERT INTO Orders VALUES (?, ?, ?, ?, ?, ?)",
            [("ORD1001", "CUST001", "P1001", "2024-10-18", "Out for Delivery", "2024-10-21"), ("ORD1002", "CUST001", "P1003", "2024-10-10", "Delivered", "2024-10-14"), ("ORD1003", "CUST002", "P1004", "2024-10-19", "Shipped", "2024-10-24")],
        )
        connection.execute("INSERT INTO CustomerMemory (customer_id, memory_key, memory_value, created_at) VALUES (?, ?, ?, datetime('now'))", ("CUST001", "preferred_category", "Headphones and running shoes"))
        connection.execute("INSERT INTO CustomerMemory (customer_id, memory_key, memory_value, created_at) VALUES (?, ?, ?, datetime('now'))", ("CUST001", "preferred_budget", "Below ₹3000"))
    connection.execute("DELETE FROM Products WHERE product_id IN ('P1002', 'P1005', 'P1007', 'P1008', 'P1009', 'P1010', 'P1011', 'P1012')")
    connection.executemany(
        "INSERT OR IGNORE INTO Products VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
        ],
    )
    connection.commit()
    connection.close()


if __name__ == "__main__":
    init_db()
    print(f"Database ready at {DB_PATH}")
