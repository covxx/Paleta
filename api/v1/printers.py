"""
Printers API v1

Handles all printer-related API endpoints with proper versioning and error handling.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from services.printer_service import PrinterService
from utils.api_utils import APIResponse, handle_api_error, validate_request_data, log_api_request

printers_bp = Blueprint('printers_v1', __name__, url_prefix='/api/v1/printers')


def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if not session.get('admin_logged_in'):
            return APIResponse.unauthorized("Admin authentication required")
        return f(*args, **kwargs)
    return decorated_function


@printers_bp.route('', methods=['GET'])
@log_api_request
def get_printers():
    """Get all printers"""
    try:
        printers = PrinterService.get_all_printers()
        return APIResponse.success(printers, "Printers retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve printers: {str(e)}", status_code=500)


@printers_bp.route('/<int:printer_id>', methods=['GET'])
@log_api_request
def get_printer(printer_id):
    """Get a specific printer by ID"""
    try:
        printer = PrinterService.get_printer_by_id(printer_id)
        if not printer:
            return APIResponse.not_found("Printer")
        return APIResponse.success(printer, "Printer retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve printer: {str(e)}", status_code=500)


@printers_bp.route('', methods=['POST'])
@admin_required
@log_api_request
def create_printer():
    """Create a new printer"""
    try:
        data = validate_request_data(['name', 'ip_address'], ['port', 'printer_type', 'label_width', 'label_height', 'dpi'])
        result = PrinterService.create_printer(data)
        return APIResponse.success(result, "Printer created successfully", status_code=201)
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to create printer: {str(e)}", status_code=500)


@printers_bp.route('/<int:printer_id>', methods=['PUT'])
@admin_required
@log_api_request
def update_printer(printer_id):
    """Update an existing printer"""
    try:
        data = validate_request_data(optional_fields=['name', 'ip_address', 'port', 'printer_type', 'label_width', 'label_height', 'dpi'])
        result = PrinterService.update_printer(printer_id, data)
        return APIResponse.success(result, "Printer updated successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to update printer: {str(e)}", status_code=500)


@printers_bp.route('/<int:printer_id>', methods=['DELETE'])
@admin_required
@log_api_request
def delete_printer(printer_id):
    """Delete a printer"""
    try:
        result = PrinterService.delete_printer(printer_id)
        return APIResponse.success(result, "Printer deleted successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to delete printer: {str(e)}", status_code=500)


@printers_bp.route('/<int:printer_id>/test', methods=['POST'])
@admin_required
@log_api_request
def test_printer(printer_id):
    """Test printer connection"""
    try:
        result = PrinterService.test_printer_connection(printer_id)
        return APIResponse.success(result, "Printer test completed")
    except Exception as e:
        return APIResponse.error(f"Failed to test printer: {str(e)}", status_code=500)


@printers_bp.route('/<int:printer_id>/print', methods=['POST'])
@admin_required
@log_api_request
def print_label(printer_id):
    """Print a label to a specific printer"""
    try:
        data = validate_request_data(['item_name', 'lot_code'], ['expiry_date', 'quantity', 'unit'])
        result = PrinterService.print_label(printer_id, data)
        return APIResponse.success(result, "Label printed successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to print label: {str(e)}", status_code=500)


@printers_bp.route('/statistics', methods=['GET'])
@log_api_request
def get_printer_statistics():
    """Get printer statistics"""
    try:
        stats = PrinterService.get_printer_statistics()
        return APIResponse.success(stats, "Printer statistics retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve printer statistics: {str(e)}", status_code=500)


@printers_bp.route('/bulk-test', methods=['POST'])
@admin_required
@log_api_request
def bulk_test_printers():
    """Test connections to all printers"""
    try:
        result = PrinterService.bulk_test_connections()
        return APIResponse.success(result, "Bulk printer test completed")
    except Exception as e:
        return APIResponse.error(f"Failed to bulk test printers: {str(e)}", status_code=500)
