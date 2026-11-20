Canteen Pre-Ordering System

A command-line Canteen Pre-Ordering System built with Python 3 and SQLite. Students pre-order food for a pickup time slot, and canteen staff manage the menu, stock and order status.

Problem Statement and Objectives

In a college canteen, students queue for long periods during breaks, orders are taken verbally or on paper, items run out without warning and staff cannot predict demand. This causes wasted break time, order mix-ups and food wastage.

Objectives:

Maintain a digital menu with prices and daily stock.
Register students and let them place orders for a pickup slot.
Generate a token number and total bill for every order.
Track order status: Placed, Preparing, Ready, Collected or Cancelled.
Validate all input and prevent invalid orders (no stock, slot full, bad data).
Features / Modules Implemented
Module	Features
cps/menu.py	Add, list, search, update stock, remove menu items
cps/students.py	Register and list students
cps/orders.py	Place order (stock update, token, total), view, cancel, status tracking, pending list
cps/validators.py	Input validation for all fields
cps/database.py	SQLite connection and schema
main.py	Interactive menu with error handling

Business rules: canteen hours 08:00-17:00 with 15-minute pickup slots; max 10 orders per slot; max 10 units of an item per order; stock reduced on order and restored on cancellation; status moves Placed -> Preparing -> Ready -> Collected; only Placed orders can be cancelled; an item in an active order cannot be removed.

Technology Stack and Tools
Python 3 (standard library only: sqlite3, unittest, datetime, re)
SQLite 3
Git and GitHub
Prerequisites and Installation
Install Python 3.8 or later (python --version).
Install Git.
Clone the repository:
git clone https://github.com/sanjaycodex/canteen-pre-ordering-system.git
cd canteen-pre-ordering-system

No external packages are needed.

How to Run
python main.py

The database file canteen.db is created automatically on first run. Choose options from the numbered menu; enter 0 to exit.

Sample Input and Output
Enter choice: 1
Item name: Veg Sandwich
Price (Rs.): 30
Stock: 10
Item added with ID 1.

Enter choice: 8
Student ID: 1
Pickup time (HH:MM, 15-min slots, 08:00-17:00): 12:15
Item ID (blank to finish): 1
Quantity: 2
Item ID (blank to finish):
Order placed!
Token #1 | Asha Nair | Pickup 12:15 | Status: Placed
  Veg Sandwich           x2  Rs. 60
  Total bill: Rs. 60

Enter choice: 6
Name: Ravi
Register number: 250391002
Phone (10 digits): 123
Error: Phone number must be exactly 10 digits.
Testing Performed and Results

Run: python -m unittest -v

20 tests cover validators (4), menu (5), students (2) and orders (9: stock update, insufficient stock, full slot, total bill, cancellation, status flow, invalid status jumps). Result: 20 tests run, 20 passed, 0 failed. The main menu options were also tested manually with valid and invalid input.

Team Member Details and Contributions

Individual project - [Your Name] ([Register Number]): design, implementation, testing, documentation and Git workflow.

Known Limitations
Command-line interface only; one user at a time.
No login or authentication for students or canteen staff.
Payment is not handled; the bill is calculated only.
Pickup time is not checked against the current clock time.
Possible Future Enhancements
Web or mobile front end (Flask / Tkinter).
Separate student and staff logins with roles.
Online payment and wallet integration.
SMS / e-mail notification when an order is ready.
Daily sales report export to CSV/PDF and popular-item analytics.
References

Python docs (docs.python.org), SQLite docs (sqlite.org/docs.html), Pro Git book (git-scm.com/book).
