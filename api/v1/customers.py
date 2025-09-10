"""
Customers API v1

Handles all customer-related API endpoints with proper versioning and error handling.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from services.customer_service import CustomerService
from utils.api_utils import APIResponse, handle_api_error, validate_request_data, log_api_request

customers_bp = Blueprint('customers_v1', __name__, url_prefix='/api/v1/customers')


def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if not session.get('admin_logged_in'):
            return APIResponse.unauthorized("Admin authentication required")
        return f(*args, **kwargs)
    return decorated_function


@customers_bp.route('', methods=['GET'])
@log_api_request
def get_customers():
    """Get all customers"""
    try:
        customers = CustomerService.get_all_customers()
        return APIResponse.success(customers, "Customers retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve customers: {str(e)}", status_code=500)


@customers_bp.route('/<int:customer_id>', methods=['GET'])
@log_api_request
def get_customer(customer_id):
    """Get a specific customer by ID"""
    try:
        customer = CustomerService.get_customer_by_id(customer_id)
        if not customer:
            return APIResponse.not_found("Customer")
        return APIResponse.success(customer, "Customer retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve customer: {str(e)}", status_code=500)


@customers_bp.route('', methods=['POST'])
@admin_required
@log_api_request
def create_customer():
    """Create a new customer"""
    try:
        data = validate_request_data(['name'], ['email', 'phone', 'address', 'quickbooks_id'])
        result = CustomerService.create_customer(data)
        return APIResponse.success(result, "Customer created successfully", status_code=201)
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to create customer: {str(e)}", status_code=500)


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@admin_required
@log_api_request
def update_customer(customer_id):
    """Update an existing customer"""
    try:
        data = validate_request_data(optional_fields=['name', 'email', 'phone', 'address', 'quickbooks_id'])
        result = CustomerService.update_customer(customer_id, data)
        return APIResponse.success(result, "Customer updated successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to update customer: {str(e)}", status_code=500)


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@admin_required
@log_api_request
def delete_customer(customer_id):
    """Delete a customer"""
    try:
        result = CustomerService.delete_customer(customer_id)
        return APIResponse.success(result, "Customer deleted successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to delete customer: {str(e)}", status_code=500)


@customers_bp.route('/statistics', methods=['GET'])
@log_api_request
def get_customer_statistics():
    """Get customer statistics"""
    try:
        stats = CustomerService.get_customer_statistics()
        return APIResponse.success(stats, "Customer statistics retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve customer statistics: {str(e)}", status_code=500)


@customers_bp.route('/search', methods=['GET'])
@log_api_request
def search_customers():
    """Search customers by name, email, or phone"""
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return APIResponse.error("Search term is required", 'VALIDATION_ERROR', 400)
        
        customers = CustomerService.search_customers(search_term)
        return APIResponse.success(customers, f"Search results for '{search_term}' retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to search customers: {str(e)}", status_code=500)


@customers_bp.route('/quickbooks-sync', methods=['GET'])
@log_api_request
def get_customers_by_sync_status():
    """Get customers filtered by QuickBooks sync status"""
    try:
        synced = request.args.get('synced', 'true').lower() == 'true'
        customers = CustomerService.get_customers_by_quickbooks_sync_status(synced)
        return APIResponse.success(customers, f"Customers with sync status '{synced}' retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve customers by sync status: {str(e)}", status_code=500)


@customers_bp.route('/bulk-update-quickbooks', methods=['POST'])
@admin_required
@log_api_request
def bulk_update_quickbooks_ids():
    """Bulk update QuickBooks IDs for customers"""
    try:
        data = validate_request_data(['updates'])
        if not isinstance(data['updates'], list):
            return APIResponse.error("Updates must be a list", 'VALIDATION_ERROR', 400)
        
        result = CustomerService.bulk_update_quickbooks_ids(data['updates'])
        return APIResponse.success(result, "QuickBooks IDs updated successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to bulk update QuickBooks IDs: {str(e)}", status_code=500)
