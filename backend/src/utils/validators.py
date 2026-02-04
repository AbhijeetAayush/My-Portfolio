import re
from .errors import ValidationError


def validate_email(email):
    """Validate email format"""
    if not email:
        raise ValidationError("Email is required")
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")
    return email.lower().strip()


def validate_password(password):
    """Validate password strength"""
    if not password:
        raise ValidationError("Password is required")
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters")
    return password


def validate_required(value, field_name):
    """Validate required field"""
    if not value or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"{field_name} is required")
    return value


def validate_slug(slug):
    """Validate URL slug format"""
    if not slug:
        raise ValidationError("Slug is required")
    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    if not re.match(pattern, slug):
        raise ValidationError("Invalid slug format. Use lowercase letters, numbers, and hyphens only")
    return slug
