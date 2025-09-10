"""
Items API v1

Handles all item-related API endpoints with proper versioning and error handling.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from services.inventory_service import InventoryService
from utils.api_utils import APIResponse, handle_api_error, validate_request_data, log_api_request

items_bp = Blueprint('items_v1', __name__, url_prefix='/api/v1/items')

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if not session.get('admin_logged_in'):
            return APIResponse.unauthorized("Admin authentication required")
        return f(*args, **kwargs)
    return decorated_function

@items_bp.route('', methods=['GET'])
@log_api_request
def get_items():
    """Get all items"""
    try:
        items = InventoryService.get_all_items()
        return APIResponse.success(items, "Items retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve items: {str(e)}", status_code=500)

@items_bp.route('/<int:item_id>', methods=['GET'])
@log_api_request
def get_item(item_id):
    """Get a specific item by ID"""
    try:
        item = InventoryService.get_item_by_id(item_id)
        if not item:
            return APIResponse.not_found("Item")
        return APIResponse.success(item, "Item retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve item: {str(e)}", status_code=500)

@items_bp.route('', methods=['POST'])
@admin_required
@log_api_request
def create_item():
    """Create a new item"""
    try:
        data = validate_request_data(['name'], ['item_code', 'gtin', 'category', 'description', 'unit_price', 'quickbooks_id'])
        result = InventoryService.create_item(data)
        return APIResponse.success(result, "Item created successfully", status_code=201)
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to create item: {str(e)}", status_code=500)

@items_bp.route('/<int:item_id>', methods=['PUT'])
@admin_required
@log_api_request
def update_item(item_id):
    """Update an existing item"""
    try:
        data = validate_request_data(optional_fields=['name', 'item_code', 'gtin', 'category', 'description', 'unit_price', 'quickbooks_id'])
        result = InventoryService.update_item(item_id, data)
        return APIResponse.success(result, "Item updated successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to update item: {str(e)}", status_code=500)

@items_bp.route('/<int:item_id>', methods=['DELETE'])
@admin_required
@log_api_request
def delete_item(item_id):
    """Delete an item"""
    try:
        result = InventoryService.delete_item(item_id)
        return APIResponse.success(result, "Item deleted successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to delete item: {str(e)}", status_code=500)

@items_bp.route('/statistics', methods=['GET'])
@log_api_request
def get_item_statistics():
    """Get item statistics"""
    try:
        stats = InventoryService.get_inventory_statistics()
        return APIResponse.success(stats, "Item statistics retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve statistics: {str(e)}", status_code=500)
