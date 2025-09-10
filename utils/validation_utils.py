"""
Validation Utilities

Provides data validation functions for common data types and formats.
"""

import re
import socket
from typing import List, Dict, Any, Optional
from datetime import datetime, date


def validate_email(email: str) -> bool:
    """Validate email address format"""
    if not email or not isinstance(email, str):
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits_only) <= 15


def validate_ip_address(ip: str) -> bool:
    """Validate IP address format"""
    if not ip or not isinstance(ip, str):
        return False
    
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def validate_port(port: Any) -> bool:
    """Validate port number"""
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False


def validate_gtin(gtin: str) -> bool:
    """Validate GTIN (Global Trade Item Number) format"""
    if not gtin or not isinstance(gtin, str):
        return False
    
    # Remove any non-digit characters
    digits = re.sub(r'\D', '', gtin)
    
    # GTIN can be 8, 12, 13, or 14 digits
    if len(digits) not in [8, 12, 13, 14]:
        return False
    
    # Basic format validation (could add checksum validation)
    return digits.isdigit()


def validate_date_format(date_string: str, format: str = '%Y-%m-%d') -> bool:
    """Validate date string format"""
    if not date_string or not isinstance(date_string, str):
        return False
    
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False


def validate_future_date(date_string: str, format: str = '%Y-%m-%d') -> bool:
    """Validate that date is in the future"""
    if not validate_date_format(date_string, format):
        return False
    
    try:
        input_date = datetime.strptime(date_string, format).date()
        return input_date > date.today()
    except ValueError:
        return False


def validate_past_date(date_string: str, format: str = '%Y-%m-%d') -> bool:
    """Validate that date is in the past"""
    if not validate_date_format(date_string, format):
        return False
    
    try:
        input_date = datetime.strptime(date_string, format).date()
        return input_date < date.today()
    except ValueError:
        return False


def validate_positive_number(value: Any) -> bool:
    """Validate that value is a positive number"""
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False


def validate_non_negative_number(value: Any) -> bool:
    """Validate that value is a non-negative number"""
    try:
        num = float(value)
        return num >= 0
    except (ValueError, TypeError):
        return False


def validate_string_length(text: str, min_length: int = 0, max_length: int = None) -> bool:
    """Validate string length"""
    if not isinstance(text, str):
        return False
    
    if len(text) < min_length:
        return False
    
    if max_length is not None and len(text) > max_length:
        return False
    
    return True


def validate_alphanumeric(text: str, allow_spaces: bool = True) -> bool:
    """Validate that text contains only alphanumeric characters"""
    if not isinstance(text, str):
        return False
    
    if allow_spaces:
        pattern = r'^[a-zA-Z0-9\s]+$'
    else:
        pattern = r'^[a-zA-Z0-9]+$'
    
    return bool(re.match(pattern, text))


def validate_currency(amount: Any) -> bool:
    """Validate currency amount"""
    try:
        num = float(amount)
        # Check if it's a valid currency amount (positive, max 2 decimal places)
        return num >= 0 and round(num, 2) == num
    except (ValueError, TypeError):
        return False


def validate_printer_type(printer_type: str) -> bool:
    """Validate printer type"""
    valid_types = ['zebra', 'datamax', 'intermec', 'other']
    return printer_type in valid_types


def validate_dpi(dpi: Any) -> bool:
    """Validate DPI value"""
    try:
        dpi_num = int(dpi)
        valid_dpis = [203, 300, 600]
        return dpi_num in valid_dpis
    except (ValueError, TypeError):
        return False


def validate_label_dimensions(width: Any, height: Any) -> bool:
    """Validate label dimensions"""
    try:
        w = float(width)
        h = float(height)
        # Reasonable label size limits (in inches)
        return 0.5 <= w <= 12.0 and 0.5 <= h <= 12.0
    except (ValueError, TypeError):
        return False


def validate_order_status(status: str) -> bool:
    """Validate order status"""
    valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    return status in valid_statuses


def validate_lot_status(status: str) -> bool:
    """Validate lot status"""
    valid_statuses = ['active', 'inactive', 'expired', 'depleted']
    return status in valid_statuses


def validate_quickbooks_id(qb_id: str) -> bool:
    """Validate QuickBooks ID format"""
    if not qb_id or not isinstance(qb_id, str):
        return False
    
    # QuickBooks IDs are typically numeric strings
    return qb_id.isdigit() and len(qb_id) > 0


def validate_item_data(item_data: Dict) -> List[str]:
    """Validate item data"""
    errors = []
    
    # Required fields
    if not item_data.get('name'):
        errors.append("Item name is required")
    elif not validate_string_length(item_data['name'], 1, 100):
        errors.append("Item name must be 1-100 characters")
    
    # Optional fields validation
    if item_data.get('item_code'):
        if not validate_string_length(item_data['item_code'], 1, 50):
            errors.append("Item code must be 1-50 characters")
    
    if item_data.get('gtin'):
        if not validate_gtin(item_data['gtin']):
            errors.append("Invalid GTIN format")
    
    if item_data.get('category'):
        if not validate_string_length(item_data['category'], 1, 50):
            errors.append("Category must be 1-50 characters")
    
    if item_data.get('unit_price'):
        if not validate_currency(item_data['unit_price']):
            errors.append("Invalid unit price format")
    
    if item_data.get('quickbooks_id'):
        if not validate_quickbooks_id(item_data['quickbooks_id']):
            errors.append("Invalid QuickBooks ID format")
    
    return errors


def validate_lot_data(lot_data: Dict) -> List[str]:
    """Validate lot data"""
    errors = []
    
    # Required fields
    if not lot_data.get('lot_code'):
        errors.append("LOT code is required")
    elif not validate_string_length(lot_data['lot_code'], 1, 50):
        errors.append("LOT code must be 1-50 characters")
    
    if not lot_data.get('item_id'):
        errors.append("Item ID is required")
    elif not isinstance(lot_data['item_id'], int) or lot_data['item_id'] <= 0:
        errors.append("Invalid item ID")
    
    if not lot_data.get('quantity'):
        errors.append("Quantity is required")
    elif not validate_positive_number(lot_data['quantity']):
        errors.append("Quantity must be a positive number")
    
    # Optional fields validation
    if lot_data.get('unit'):
        if not validate_string_length(lot_data['unit'], 1, 20):
            errors.append("Unit must be 1-20 characters")
    
    if lot_data.get('expiry_date'):
        if not validate_date_format(lot_data['expiry_date']):
            errors.append("Invalid expiry date format (use YYYY-MM-DD)")
    
    if lot_data.get('vendor_id'):
        if not isinstance(lot_data['vendor_id'], int) or lot_data['vendor_id'] <= 0:
            errors.append("Invalid vendor ID")
    
    if lot_data.get('status'):
        if not validate_lot_status(lot_data['status']):
            errors.append("Invalid lot status")
    
    return errors


def validate_customer_data(customer_data: Dict) -> List[str]:
    """Validate customer data"""
    errors = []
    
    # Required fields
    if not customer_data.get('name'):
        errors.append("Customer name is required")
    elif not validate_string_length(customer_data['name'], 1, 100):
        errors.append("Customer name must be 1-100 characters")
    
    # Optional fields validation
    if customer_data.get('email'):
        if not validate_email(customer_data['email']):
            errors.append("Invalid email format")
    
    if customer_data.get('phone'):
        if not validate_phone(customer_data['phone']):
            errors.append("Invalid phone number format")
    
    if customer_data.get('quickbooks_id'):
        if not validate_quickbooks_id(customer_data['quickbooks_id']):
            errors.append("Invalid QuickBooks ID format")
    
    return errors


def validate_printer_data(printer_data: Dict) -> List[str]:
    """Validate printer data"""
    errors = []
    
    # Required fields
    if not printer_data.get('name'):
        errors.append("Printer name is required")
    elif not validate_string_length(printer_data['name'], 1, 100):
        errors.append("Printer name must be 1-100 characters")
    
    if not printer_data.get('ip_address'):
        errors.append("IP address is required")
    elif not validate_ip_address(printer_data['ip_address']):
        errors.append("Invalid IP address format")
    
    # Optional fields validation
    if printer_data.get('port'):
        if not validate_port(printer_data['port']):
            errors.append("Invalid port number (1-65535)")
    
    if printer_data.get('printer_type'):
        if not validate_printer_type(printer_data['printer_type']):
            errors.append("Invalid printer type")
    
    if printer_data.get('dpi'):
        if not validate_dpi(printer_data['dpi']):
            errors.append("Invalid DPI value")
    
    if printer_data.get('label_width') and printer_data.get('label_height'):
        if not validate_label_dimensions(printer_data['label_width'], printer_data['label_height']):
            errors.append("Invalid label dimensions")
    
    return errors


def validate_order_data(order_data: Dict) -> List[str]:
    """Validate order data"""
    errors = []
    
    # Required fields
    if not order_data.get('customer_id'):
        errors.append("Customer ID is required")
    elif not isinstance(order_data['customer_id'], int) or order_data['customer_id'] <= 0:
        errors.append("Invalid customer ID")
    
    # Optional fields validation
    if order_data.get('status'):
        if not validate_order_status(order_data['status']):
            errors.append("Invalid order status")
    
    if order_data.get('total_amount'):
        if not validate_currency(order_data['total_amount']):
            errors.append("Invalid total amount format")
    
    if order_data.get('order_number'):
        if not validate_string_length(order_data['order_number'], 1, 50):
            errors.append("Order number must be 1-50 characters")
    
    return errors


def sanitize_string(text: str, max_length: int = None) -> str:
    """Sanitize string input"""
    if not isinstance(text, str):
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove any null bytes
    text = text.replace('\x00', '')
    
    # Truncate if max_length specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def sanitize_html(text: str) -> str:
    """Basic HTML sanitization"""
    if not isinstance(text, str):
        return ""
    
    # Remove HTML tags (basic implementation)
    import re
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode HTML entities
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    
    return text
