"""Input validation helpers. Every function returns the cleaned value
or raises ValidationError with a clear message."""
import re


class ValidationError(Exception):
    """Raised when user input is invalid."""


OPEN_MINUTES = 8 * 60      # 08:00
CLOSE_MINUTES = 17 * 60    # 17:00


def validate_name(name):
    name = (name or "").strip()
    if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]{1,49}", name):
        raise ValidationError("Name must be 2-50 letters.")
    return name


def validate_reg_no(reg_no):
    reg_no = (reg_no or "").strip()
    if not reg_no.isdigit() or not 6 <= len(reg_no) <= 15:
        raise ValidationError("Register number must be 6-15 digits.")
    return reg_no


def validate_phone(phone):
    phone = (phone or "").strip()
    if not re.fullmatch(r"\d{10}", phone):
        raise ValidationError("Phone number must be exactly 10 digits.")
    return phone


def validate_item_name(name):
    name = (name or "").strip()
    if not 2 <= len(name) <= 40:
        raise ValidationError("Item name must be 2-40 characters.")
    return name


def validate_price(price):
    try:
        price = int(price)
    except (TypeError, ValueError):
        raise ValidationError("Price must be a whole number.")
    if not 1 <= price <= 1000:
        raise ValidationError("Price must be between Rs. 1 and Rs. 1000.")
    return price


def validate_stock(stock):
    try:
        stock = int(stock)
    except (TypeError, ValueError):
        raise ValidationError("Stock must be a whole number.")
    if not 0 <= stock <= 500:
        raise ValidationError("Stock must be between 0 and 500.")
    return stock


def validate_quantity(qty):
    try:
        qty = int(qty)
    except (TypeError, ValueError):
        raise ValidationError("Quantity must be a whole number.")
    if not 1 <= qty <= 10:
        raise ValidationError("Quantity must be between 1 and 10.")
    return qty


def validate_id(value, label="ID"):
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{label} must be a positive number.")
    if value < 1:
        raise ValidationError(f"{label} must be a positive number.")
    return value


def validate_slot(slot):
    """Pickup slot as HH:MM, 08:00-17:00, on a 15-minute step."""
    slot = (slot or "").strip()
    match = re.fullmatch(r"(\d{1,2}):(\d{2})", slot)
    if not match:
        raise ValidationError("Pickup time must be in HH:MM format.")
    hours, minutes = int(match.group(1)), int(match.group(2))
    total = hours * 60 + minutes
    if minutes > 59 or not OPEN_MINUTES <= total <= CLOSE_MINUTES:
        raise ValidationError("Pickup time must be between 08:00 and 17:00.")
    if minutes % 15 != 0:
        raise ValidationError("Pickup time must be a 15-minute slot (e.g. 12:15).")
    return f"{hours:02d}:{minutes:02d}"
