"""Input validation helpers."""
import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email: str) -> tuple[bool, str]:
    if not email or not isinstance(email, str):
        return False, "Email is required."
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        return False, "Invalid email format."
    return True, email


def validate_password(password: str, min_length: int = 8) -> tuple[bool, str]:
    if not password:
        return False, "Password is required."
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters."
    return True, ""


def validate_full_name(full_name: str) -> tuple[bool, str]:
    if not full_name or not str(full_name).strip():
        return False, "Full name is required."
    return True, str(full_name).strip()
