"""Populate the demo SQLite database with a small sales dataset."""

import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "sales.db"


def seed() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.executescript(
            """
            DROP TABLE IF EXISTS order_items;
            DROP TABLE IF EXISTS orders;
            DROP TABLE IF EXISTS products;

            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                unit_price REAL NOT NULL
            );

            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                customer TEXT NOT NULL,
                channel TEXT NOT NULL,
                total REAL NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE order_items (
                id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(id),
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity INTEGER NOT NULL,
                line_total REAL NOT NULL
            );
            """
        )

        products = [
            (1, "Wireless Mouse", "Accessories", 29.0),
            (2, "Mechanical Keyboard", "Accessories", 99.0),
            (3, "4K Monitor", "Displays", 399.0),
            (4, "USB-C Hub", "Accessories", 49.0),
            (5, "Noise Cancelling Headphones", "Audio", 199.0),
        ]
        cur.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)

        orders = [
            (1, "Acme Corp", "web", 726.0, "2024-06-01"),
            (2, "Orbit Goods", "sales", 248.0, "2024-06-03"),
            (3, "Wayfinder", "web", 428.0, "2024-06-10"),
            (4, "Brightline", "partner", 1497.0, "2024-07-02"),
            (5, "Orbit Goods", "web", 228.0, "2024-07-15"),
        ]
        cur.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders)

        items = [
            (1, 1, 2, 3, 297.0),
            (2, 1, 4, 3, 147.0),
            (3, 1, 5, 2, 398.0),
            (4, 2, 1, 2, 58.0),
            (5, 2, 4, 2, 98.0),
            (6, 2, 5, 1, 199.0),
            (7, 3, 3, 1, 399.0),
            (8, 3, 1, 1, 29.0),
            (9, 4, 3, 3, 1197.0),
            (10, 4, 2, 2, 198.0),
            (11, 4, 4, 2, 98.0),
            (12, 4, 5, 1, 199.0),
            (13, 5, 1, 2, 58.0),
            (14, 5, 4, 2, 98.0),
            (15, 5, 2, 1, 99.0),
        ]
        cur.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", items)

        conn.commit()
        print(f"Seeded demo database at {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    seed()
