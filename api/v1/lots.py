"""
LOTs API v1

Handles all LOT-related API endpoints with proper versioning and error handling.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from services.inventory_service import InventoryService
from utils.api_utils import APIResponse, handle_api_error, validate_request_data, log_api_request

lots_bp = Blueprint('lots_v1', __name__, url_prefix='/api/v1/lots')

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if not session.get('admin_logged_in'):
            return APIResponse.unauthorized("Admin authentication required")
        return f(*args, **kwargs)
    return decorated_function

@lots_bp.route('', methods=['GET'])
@log_api_request
def get_lots():
    """Get all lots"""
    try:
        lots = InventoryService.get_all_lots()
        return APIResponse.success(lots, "LOTs retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve lots: {str(e)}", status_code=500)

@lots_bp.route('/<int:lot_id>', methods=['GET'])
@log_api_request
def get_lot(lot_id):
    """Get a specific lot by ID"""
    try:
        lot = InventoryService.get_lot_by_id(lot_id)
        if not lot:
            return APIResponse.not_found("LOT")
        return APIResponse.success(lot, "LOT retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve lot: {str(e)}", status_code=500)

@lots_bp.route('', methods=['POST'])
@admin_required
@log_api_request
def create_lot():
    """Create a new lot"""
    try:
        data = validate_request_data(['lot_code', 'item_id', 'quantity'], ['unit', 'expiry_date', 'vendor_id', 'status'])
        result = InventoryService.create_lot(data)
        return APIResponse.success(result, "LOT created successfully", status_code=201)
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to create lot: {str(e)}", status_code=500)

@lots_bp.route('/<int:lot_id>', methods=['PUT'])
@admin_required
@log_api_request
def update_lot(lot_id):
    """Update an existing lot"""
    try:
        data = validate_request_data(optional_fields=['lot_code', 'quantity', 'unit', 'expiry_date', 'vendor_id', 'status'])
        result = InventoryService.update_lot(lot_id, data)
        return APIResponse.success(result, "LOT updated successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to update lot: {str(e)}", status_code=500)

@lots_bp.route('/<int:lot_id>', methods=['DELETE'])
@admin_required
@log_api_request
def delete_lot(lot_id):
    """Delete a lot"""
    try:
        result = InventoryService.delete_lot(lot_id)
        return APIResponse.success(result, "LOT deleted successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to delete lot: {str(e)}", status_code=500)

@lots_bp.route('/expiring', methods=['GET'])
@log_api_request
def get_expiring_lots():
    """Get lots expiring within specified days"""
    try:
        days = request.args.get('days', 7, type=int)
        lots = InventoryService.get_expiring_lots(days)
        return APIResponse.success(lots, f"Expiring lots retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve expiring lots: {str(e)}", status_code=500)
