"""Database connection and schema for the Canteen Pre-Ordering System."""
import sqlite3

DB_FILE = "canteen.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS menu_items (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL UNIQUE COLLATE NOCASE,
    price INTEGER NOT NULL CHECK (price > 0),
    stock INTEGER NOT NULL CHECK (stock >= 0)
);
CREATE TABLE IF NOT EXISTS students (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name   TEXT NOT NULL,
    reg_no TEXT NOT NULL UNIQUE,
    phone  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id),
    order_date TEXT NOT NULL,
    slot       TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'Placed',
    total      INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS order_items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   INTEGER NOT NULL REFERENCES orders(id),
    item_id    INTEGER NOT NULL REFERENCES menu_items(id),
    quantity   INTEGER NOT NULL,
    unit_price INTEGER NOT NULL
);
"""


def get_connection(path=DB_FILE):
    """Open a connection (use ':memory:' for tests) and create the tables."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn
