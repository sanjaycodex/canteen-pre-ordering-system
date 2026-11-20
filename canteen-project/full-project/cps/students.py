"""Student registration and lookup."""
import sqlite3

from cps.validators import (ValidationError, validate_id, validate_name,
                            validate_phone, validate_reg_no)


def register_student(conn, name, reg_no, phone):
    name = validate_name(name)
    reg_no = validate_reg_no(reg_no)
    phone = validate_phone(phone)
    try:
        cur = conn.execute(
            "INSERT INTO students (name, reg_no, phone) VALUES (?, ?, ?)",
            (name, reg_no, phone))
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValidationError("A student with this register number already exists.")
    return cur.lastrowid


def list_students(conn):
    return conn.execute("SELECT * FROM students ORDER BY id").fetchall()


def get_student(conn, student_id):
    student_id = validate_id(student_id, "Student ID")
    row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if row is None:
        raise ValidationError(f"No student with ID {student_id}.")
    return row
