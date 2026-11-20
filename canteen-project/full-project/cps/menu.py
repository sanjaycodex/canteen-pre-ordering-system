"""Menu management: add, list, search, update stock and remove items."""
import sqlite3

from cps.validators import (ValidationError, validate_id, validate_item_name,
                            validate_price, validate_stock)

ACTIVE_STATUSES = ("Placed", "Preparing", "Ready")


def add_item(conn, name, price, stock):
    name = validate_item_name(name)
    price = validate_price(price)
    stock = validate_stock(stock)
    try:
        cur = conn.execute(
            "INSERT INTO menu_items (name, price, stock) VALUES (?, ?, ?)",
            (name, price, stock))
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValidationError("An item with this name already exists.")
    return cur.lastrowid


def list_items(conn):
    return conn.execute("SELECT * FROM menu_items ORDER BY id").fetchall()


def search_items(conn, keyword):
    keyword = (keyword or "").strip()
    if not keyword:
        raise ValidationError("Search keyword cannot be empty.")
    return conn.execute(
        "SELECT * FROM menu_items WHERE name LIKE ? ORDER BY id",
        (f"%{keyword}%",)).fetchall()


def get_item(conn, item_id):
    item_id = validate_id(item_id, "Item ID")
    row = conn.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        raise ValidationError(f"No menu item with ID {item_id}.")
    return row


def update_stock(conn, item_id, stock):
    item = get_item(conn, item_id)
    stock = validate_stock(stock)
    conn.execute("UPDATE menu_items SET stock = ? WHERE id = ?", (stock, item["id"]))
    conn.commit()


def remove_item(conn, item_id):
    item = get_item(conn, item_id)
    marks = ",".join("?" * len(ACTIVE_STATUSES))
    active = conn.execute(
        "SELECT COUNT(*) FROM order_items oi JOIN orders o ON o.id = oi.order_id "
        f"WHERE oi.item_id = ? AND o.status IN ({marks})",
        (item["id"], *ACTIVE_STATUSES)).fetchone()[0]
    if active:
        raise ValidationError("Item is part of an active order and cannot be removed.")
    used = conn.execute("SELECT COUNT(*) FROM order_items WHERE item_id = ?",
                        (item["id"],)).fetchone()[0]
    if used:
        # Keep history intact: past orders still refer to this item.
        conn.execute("UPDATE menu_items SET stock = 0 WHERE id = ?", (item["id"],))
        conn.commit()
        raise ValidationError("Item appears in past orders; its stock was set to 0 instead of deleting.")
    conn.execute("DELETE FROM menu_items WHERE id = ?", (item["id"],))
    conn.commit()
