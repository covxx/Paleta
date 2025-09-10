"""
Orders API v1

Handles all order-related API endpoints with proper versioning and error handling.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from services.order_service import OrderService
from utils.api_utils import APIResponse, handle_api_error, validate_request_data, log_api_request

orders_bp = Blueprint('orders_v1', __name__, url_prefix='/api/v1/orders')


def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if not session.get('admin_logged_in'):
            return APIResponse.unauthorized("Admin authentication required")
        return f(*args, **kwargs)
    return decorated_function


@orders_bp.route('', methods=['GET'])
@log_api_request
def get_orders():
    """Get all orders"""
    try:
        orders = OrderService.get_all_orders()
        return APIResponse.success(orders, "Orders retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve orders: {str(e)}", status_code=500)


@orders_bp.route('/<int:order_id>', methods=['GET'])
@log_api_request
def get_order(order_id):
    """Get a specific order by ID"""
    try:
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return APIResponse.not_found("Order")
        return APIResponse.success(order, "Order retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve order: {str(e)}", status_code=500)


@orders_bp.route('', methods=['POST'])
@admin_required
@log_api_request
def create_order():
    """Create a new order"""
    try:
        data = validate_request_data(['customer_id'], ['order_number', 'status', 'total_amount', 'quickbooks_synced'])
        result = OrderService.create_order(data)
        return APIResponse.success(result, "Order created successfully", status_code=201)
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to create order: {str(e)}", status_code=500)


@orders_bp.route('/<int:order_id>', methods=['PUT'])
@admin_required
@log_api_request
def update_order(order_id):
    """Update an existing order"""
    try:
        data = validate_request_data(optional_fields=['order_number', 'customer_id', 'status', 'total_amount', 'quickbooks_synced'])
        result = OrderService.update_order(order_id, data)
        return APIResponse.success(result, "Order updated successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to update order: {str(e)}", status_code=500)


@orders_bp.route('/<int:order_id>', methods=['DELETE'])
@admin_required
@log_api_request
def delete_order(order_id):
    """Delete an order"""
    try:
        result = OrderService.delete_order(order_id)
        return APIResponse.success(result, "Order deleted successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to delete order: {str(e)}", status_code=500)


@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@admin_required
@log_api_request
def update_order_status(order_id):
    """Update order status"""
    try:
        data = validate_request_data(['status'])
        result = OrderService.update_order_status(order_id, data['status'])
        return APIResponse.success(result, "Order status updated successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to update order status: {str(e)}", status_code=500)


@orders_bp.route('/status/<status>', methods=['GET'])
@log_api_request
def get_orders_by_status(status):
    """Get orders filtered by status"""
    try:
        orders = OrderService.get_orders_by_status(status)
        return APIResponse.success(orders, f"Orders with status '{status}' retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve orders: {str(e)}", status_code=500)


@orders_bp.route('/customer/<int:customer_id>', methods=['GET'])
@log_api_request
def get_orders_by_customer(customer_id):
    """Get orders for a specific customer"""
    try:
        orders = OrderService.get_orders_by_customer(customer_id)
        return APIResponse.success(orders, f"Orders for customer {customer_id} retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve customer orders: {str(e)}", status_code=500)


@orders_bp.route('/statistics', methods=['GET'])
@log_api_request
def get_order_statistics():
    """Get order statistics"""
    try:
        stats = OrderService.get_order_statistics()
        return APIResponse.success(stats, "Order statistics retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve order statistics: {str(e)}", status_code=500)


@orders_bp.route('/search', methods=['GET'])
@log_api_request
def search_orders():
    """Search orders by order number or customer name"""
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return APIResponse.error("Search term is required", 'VALIDATION_ERROR', 400)
        
        orders = OrderService.search_orders(search_term)
        return APIResponse.success(orders, f"Search results for '{search_term}' retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to search orders: {str(e)}", status_code=500)
