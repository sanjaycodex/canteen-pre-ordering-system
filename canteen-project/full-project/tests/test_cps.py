"""Unit tests for the Canteen Pre-Ordering System (run: python -m unittest -v)."""
import unittest

from cps import menu, orders, students
from cps.database import get_connection
from cps.validators import (ValidationError, validate_name, validate_phone,
                            validate_reg_no, validate_slot)

TODAY = "2026-11-20"


class BaseCase(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(":memory:")

    def tearDown(self):
        self.conn.close()

    def make_student(self, reg="250391001", name="Asha Nair", phone="9876543210"):
        return students.register_student(self.conn, name, reg, phone)

    def make_item(self, name="Veg Sandwich", price=30, stock=10):
        return menu.add_item(self.conn, name, price, stock)

    def stock_of(self, item_id):
        return menu.get_item(self.conn, item_id)["stock"]


class ValidatorTests(unittest.TestCase):
    def test_name_invalid(self):
        with self.assertRaises(ValidationError):
            validate_name("A1")
        self.assertEqual(validate_name("  Ravi Kumar "), "Ravi Kumar")

    def test_reg_no_must_be_digits(self):
        with self.assertRaises(ValidationError):
            validate_reg_no("25AB1234")
        self.assertEqual(validate_reg_no("250391001"), "250391001")

    def test_phone_must_be_10_digits(self):
        with self.assertRaises(ValidationError):
            validate_phone("12345")
        self.assertEqual(validate_phone("9876543210"), "9876543210")

    def test_slot_rules(self):
        for bad in ("07:45", "17:15", "12:10", "noon", "12:75"):
            with self.assertRaises(ValidationError):
                validate_slot(bad)
        self.assertEqual(validate_slot("9:15"), "09:15")


class MenuTests(BaseCase):
    def test_add_and_list(self):
        self.make_item("Tea", 10, 50)
        rows = menu.list_items(self.conn)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "Tea")

    def test_duplicate_item_rejected(self):
        self.make_item("Tea")
        with self.assertRaises(ValidationError):
            self.make_item("tea")

    def test_invalid_price(self):
        with self.assertRaises(ValidationError):
            menu.add_item(self.conn, "Coffee", 0, 5)
        with self.assertRaises(ValidationError):
            menu.add_item(self.conn, "Coffee", "abc", 5)

    def test_search_case_insensitive(self):
        self.make_item("Masala Dosa", 40, 10)
        self.make_item("Tea", 10, 10)
        self.assertEqual(len(menu.search_items(self.conn, "DOSA")), 1)

    def test_remove_item(self):
        free = self.make_item("Tea")
        menu.remove_item(self.conn, free)
        self.assertEqual(menu.list_items(self.conn), [])
        used = self.make_item("Samosa")
        sid = self.make_student()
        orders.place_order(self.conn, sid, "12:00", [(used, 1)], today=TODAY)
        with self.assertRaises(ValidationError):
            menu.remove_item(self.conn, used)


class StudentTests(BaseCase):
    def test_duplicate_reg_no_rejected(self):
        self.make_student()
        with self.assertRaises(ValidationError):
            self.make_student(name="Someone Else")

    def test_unknown_student(self):
        with self.assertRaises(ValidationError):
            students.get_student(self.conn, 99)


class OrderTests(BaseCase):
    def setUp(self):
        super().setUp()
        self.sid = self.make_student()
        self.item = self.make_item("Veg Sandwich", 30, 10)

    def place(self, qty=2, slot="12:15"):
        return orders.place_order(self.conn, self.sid, slot, [(self.item, qty)], today=TODAY)

    def test_stock_decreases_on_order(self):
        self.place(3)
        self.assertEqual(self.stock_of(self.item), 7)

    def test_insufficient_stock(self):
        with self.assertRaises(ValidationError):
            self.place(11)
        small = self.make_item("Juice", 20, 1)
        with self.assertRaises(ValidationError):
            orders.place_order(self.conn, self.sid, "12:15", [(small, 2)], today=TODAY)

    def test_slot_full(self):
        menu.update_stock(self.conn, self.item, 50)
        for _ in range(orders.MAX_ORDERS_PER_SLOT):
            self.place(1)
        with self.assertRaises(ValidationError):
            self.place(1)
        self.place(1, slot="12:30")     # a different slot still works

    def test_total_calculated_correctly(self):
        tea = self.make_item("Tea", 10, 20)
        oid = orders.place_order(self.conn, self.sid, "12:15",
                                 [(self.item, 2), (tea, 3)], today=TODAY)
        order, lines = orders.get_order(self.conn, oid)
        self.assertEqual(order["total"], 2 * 30 + 3 * 10)
        self.assertEqual(orders.calculate_total([(30, 2), (10, 3)]), 90)
        self.assertEqual(len(lines), 2)

    def test_cancel_restores_stock(self):
        oid = self.place(4)
        orders.cancel_order(self.conn, oid)
        self.assertEqual(self.stock_of(self.item), 10)
        self.assertEqual(orders.get_order(self.conn, oid)[0]["status"], "Cancelled")

    def test_cancel_after_preparing_rejected(self):
        oid = self.place()
        orders.update_status(self.conn, oid, "Preparing")
        with self.assertRaises(ValidationError):
            orders.cancel_order(self.conn, oid)

    def test_status_flow_in_order(self):
        oid = self.place()
        for status in ("Preparing", "Ready", "Collected"):
            orders.update_status(self.conn, oid, status)
        self.assertEqual(orders.get_order(self.conn, oid)[0]["status"], "Collected")

    def test_invalid_status_jump_rejected(self):
        oid = self.place()
        with self.assertRaises(ValidationError):
            orders.update_status(self.conn, oid, "Collected")
        with self.assertRaises(ValidationError):
            orders.update_status(self.conn, oid, "Cooked")

    def test_collected_order_cannot_be_cancelled(self):
        oid = self.place()
        for status in ("Preparing", "Ready", "Collected"):
            orders.update_status(self.conn, oid, status)
        with self.assertRaises(ValidationError):
            orders.cancel_order(self.conn, oid)


if __name__ == "__main__":
    unittest.main()
