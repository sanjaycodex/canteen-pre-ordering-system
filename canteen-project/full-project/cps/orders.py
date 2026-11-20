"""Orders: placement with stock update, token and total bill; cancellation."""
from datetime import date

from cps.menu import get_item
from cps.students import get_student
from cps.validators import (ValidationError, validate_id, validate_quantity,
                            validate_slot)

MAX_ORDERS_PER_SLOT = 10
MAX_QTY_PER_ITEM = 10


def calculate_total(lines):
    """lines: list of (unit_price, quantity)."""
    return sum(price * qty for price, qty in lines)


def place_order(conn, student_id, slot, items, today=None):
    """items: list of (item_id, quantity). Returns the new order ID (token)."""
    if not items:
        raise ValidationError("An order must contain at least one item.")
    student = get_student(conn, student_id)
    slot = validate_slot(slot)
    today = today or date.today().isoformat()

    taken = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE order_date = ? AND slot = ? "
        "AND status != 'Cancelled'", (today, slot)).fetchone()[0]
    if taken >= MAX_ORDERS_PER_SLOT:
        raise ValidationError(f"Slot {slot} is full. Please choose another time.")

    wanted = {}                      # merge repeated items
    for item_id, qty in items:
        item = get_item(conn, item_id)
        wanted[item["id"]] = wanted.get(item["id"], 0) + validate_quantity(qty)

    lines = []
    for item_id, qty in wanted.items():
        item = get_item(conn, item_id)
        if qty > MAX_QTY_PER_ITEM:
            raise ValidationError(f"Maximum {MAX_QTY_PER_ITEM} units of '{item['name']}' per order.")
        if item["stock"] < qty:
            raise ValidationError(
                f"Only {item['stock']} of '{item['name']}' left in stock.")
        lines.append((item["id"], qty, item["price"]))

    total = calculate_total([(price, qty) for _, qty, price in lines])
    cur = conn.execute(
        "INSERT INTO orders (student_id, order_date, slot, total) VALUES (?, ?, ?, ?)",
        (student["id"], today, slot, total))
    order_id = cur.lastrowid
    for item_id, qty, price in lines:
        conn.execute(
            "INSERT INTO order_items (order_id, item_id, quantity, unit_price) "
            "VALUES (?, ?, ?, ?)", (order_id, item_id, qty, price))
        conn.execute("UPDATE menu_items SET stock = stock - ? WHERE id = ?",
                     (qty, item_id))
    conn.commit()
    return order_id


def get_order(conn, order_id):
    order_id = validate_id(order_id, "Order ID")
    order = conn.execute(
        "SELECT o.*, s.name AS student_name FROM orders o "
        "JOIN students s ON s.id = o.student_id WHERE o.id = ?",
        (order_id,)).fetchone()
    if order is None:
        raise ValidationError(f"No order with ID {order_id}.")
    lines = conn.execute(
        "SELECT m.name, oi.quantity, oi.unit_price FROM order_items oi "
        "JOIN menu_items m ON m.id = oi.item_id WHERE oi.order_id = ?",
        (order_id,)).fetchall()
    return order, lines


def cancel_order(conn, order_id):
    order, lines = get_order(conn, order_id)
    if order["status"] != "Placed":
        raise ValidationError(
            f"Order is '{order['status']}'; only 'Placed' orders can be cancelled.")
    for row in conn.execute(
            "SELECT item_id, quantity FROM order_items WHERE order_id = ?",
            (order["id"],)).fetchall():
        conn.execute("UPDATE menu_items SET stock = stock + ? WHERE id = ?",
                     (row["quantity"], row["item_id"]))
    conn.execute("UPDATE orders SET status = 'Cancelled' WHERE id = ?", (order["id"],))
    conn.commit()


# ---------- Order status tracking ----------
STATUS_FLOW = ["Placed", "Preparing", "Ready", "Collected"]


def update_status(conn, order_id, new_status):
    """Move an order one step forward: Placed -> Preparing -> Ready -> Collected."""
    order, _ = get_order(conn, order_id)
    new_status = (new_status or "").strip().capitalize()
    if new_status not in STATUS_FLOW:
        raise ValidationError("Status must be one of: " + ", ".join(STATUS_FLOW))
    current = order["status"]
    if current == "Cancelled":
        raise ValidationError("A cancelled order cannot be updated.")
    if STATUS_FLOW.index(new_status) != STATUS_FLOW.index(current) + 1:
        raise ValidationError(f"Cannot move from '{current}' to '{new_status}'.")
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order["id"]))
    conn.commit()


def pending_orders(conn):
    """Orders that still need action, earliest pickup slot first."""
    return conn.execute(
        "SELECT o.*, s.name AS student_name FROM orders o "
        "JOIN students s ON s.id = o.student_id "
        "WHERE o.status IN ('Placed', 'Preparing', 'Ready') "
        "ORDER BY o.slot, o.id").fetchall()
