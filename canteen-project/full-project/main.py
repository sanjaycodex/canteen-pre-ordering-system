"""Canteen Pre-Ordering System - command-line interface."""
from cps import menu, orders, students
from cps.database import get_connection
from cps.validators import ValidationError

MENU_TEXT = """
========== CANTEEN PRE-ORDERING SYSTEM ==========
 1. Add menu item          8. Place order
 2. List menu              9. View order
 3. Search menu           10. Cancel order
 4. Update stock          11. Update order status
 5. Remove menu item      12. Pending orders
 6. Register student
 7. List students
 0. Exit
=================================================
"""


def print_menu_rows(rows):
    print(f"{'ID':<4}{'Item':<24}{'Price':>6}{'Stock':>7}")
    for r in rows:
        print(f"{r['id']:<4}{r['name']:<24}{r['price']:>6}{r['stock']:>7}")
    if not rows:
        print("No items found.")


def show_order(order, lines):
    print(f"Token #{order['id']} | {order['student_name']} | "
          f"Pickup {order['slot']} | Status: {order['status']}")
    for l in lines:
        print(f"  {l['name']:<22} x{l['quantity']}  Rs. {l['unit_price'] * l['quantity']}")
    print(f"  Total bill: Rs. {order['total']}")


def add_item(conn):
    name = input("Item name: ")
    price = input("Price (Rs.): ")
    stock = input("Stock: ")
    item_id = menu.add_item(conn, name, price, stock)
    print(f"Item added with ID {item_id}.")


def update_stock(conn):
    menu.update_stock(conn, input("Item ID: "), input("New stock: "))
    print("Stock updated.")


def remove_item(conn):
    menu.remove_item(conn, input("Item ID: "))
    print("Item removed.")


def register_student(conn):
    name = input("Name: ")
    reg_no = input("Register number: ")
    phone = input("Phone (10 digits): ")
    sid = students.register_student(conn, name, reg_no, phone)
    print(f"Student registered with ID {sid}.")


def place_order(conn):
    student_id = input("Student ID: ")
    slot = input("Pickup time (HH:MM, 15-min slots, 08:00-17:00): ")
    items = []
    while True:
        item_id = input("Item ID (blank to finish): ").strip()
        if not item_id:
            break
        items.append((item_id, input("Quantity: ")))
    token = orders.place_order(conn, student_id, slot, items)
    order, lines = orders.get_order(conn, token)
    print("Order placed!")
    show_order(order, lines)


def view_order(conn):
    order, lines = orders.get_order(conn, input("Order/Token ID: "))
    show_order(order, lines)


def cancel_order(conn):
    orders.cancel_order(conn, input("Order/Token ID: "))
    print("Order cancelled and stock restored.")


def update_status(conn):
    oid = input("Order/Token ID: ")
    orders.update_status(conn, oid, input("New status (Preparing/Ready/Collected): "))
    print("Status updated.")


def pending(conn):
    rows = orders.pending_orders(conn)
    if not rows:
        print("No pending orders.")
    for r in rows:
        print(f"Token #{r['id']} | {r['slot']} | {r['student_name']} | "
              f"{r['status']} | Rs. {r['total']}")


ACTIONS = {
    "1": add_item,
    "2": lambda c: print_menu_rows(menu.list_items(c)),
    "3": lambda c: print_menu_rows(menu.search_items(c, input("Keyword: "))),
    "4": update_stock,
    "5": remove_item,
    "6": register_student,
    "7": lambda c: [print(f"{s['id']:<4}{s['name']:<20}{s['reg_no']:<16}{s['phone']}")
                    for s in students.list_students(c)],
    "8": place_order,
    "9": view_order,
    "10": cancel_order,
    "11": update_status,
    "12": pending,
}


def main():
    conn = get_connection()
    try:
        while True:
            print(MENU_TEXT)
            choice = input("Enter choice: ").strip()
            if choice == "0":
                print("Goodbye!")
                break
            action = ACTIONS.get(choice)
            if action is None:
                print("Error: Please choose a number from the menu.")
                continue
            try:
                action(conn)
            except ValidationError as err:
                print(f"Error: {err}")
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
