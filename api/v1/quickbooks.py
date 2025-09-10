"""
QuickBooks API v1

Handles all QuickBooks-related API endpoints with proper versioning and error handling.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from services.quickbooks_service import QuickBooksService
from utils.api_utils import APIResponse, handle_api_error, validate_request_data, log_api_request

quickbooks_bp = Blueprint('quickbooks_v1', __name__, url_prefix='/api/v1/quickbooks')


def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if not session.get('admin_logged_in'):
            return APIResponse.unauthorized("Admin authentication required")
        return f(*args, **kwargs)
    return decorated_function


@quickbooks_bp.route('/status', methods=['GET'])
@admin_required
@log_api_request
def get_connection_status():
    """Get QuickBooks connection status"""
    try:
        status = QuickBooksService.get_connection_status()
        return APIResponse.success(status, "Connection status retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to get connection status: {str(e)}", status_code=500)


@quickbooks_bp.route('/connect', methods=['POST'])
@admin_required
@log_api_request
def initiate_oauth_flow():
    """Initiate QuickBooks OAuth flow"""
    try:
        result = QuickBooksService.initiate_oauth_flow()
        return APIResponse.success(result, "OAuth flow initiated successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to initiate OAuth flow: {str(e)}", status_code=500)


@quickbooks_bp.route('/disconnect', methods=['POST'])
@admin_required
@log_api_request
def disconnect():
    """Disconnect from QuickBooks"""
    try:
        result = QuickBooksService.disconnect()
        return APIResponse.success(result, "Disconnected from QuickBooks successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to disconnect: {str(e)}", status_code=500)


@quickbooks_bp.route('/sync/items', methods=['POST'])
@admin_required
@log_api_request
def sync_items():
    """Sync items from QuickBooks"""
    try:
        result = QuickBooksService.sync_items()
        return APIResponse.success(result, "Items sync completed")
    except Exception as e:
        return APIResponse.error(f"Failed to sync items: {str(e)}", status_code=500)


@quickbooks_bp.route('/sync/customers', methods=['POST'])
@admin_required
@log_api_request
def sync_customers():
    """Sync customers from QuickBooks"""
    try:
        result = QuickBooksService.sync_customers()
        return APIResponse.success(result, "Customers sync completed")
    except Exception as e:
        return APIResponse.error(f"Failed to sync customers: {str(e)}", status_code=500)


@quickbooks_bp.route('/sync/statistics', methods=['GET'])
@admin_required
@log_api_request
def get_sync_statistics():
    """Get QuickBooks sync statistics"""
    try:
        stats = QuickBooksService.get_sync_statistics()
        return APIResponse.success(stats, "Sync statistics retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve sync statistics: {str(e)}", status_code=500)


@quickbooks_bp.route('/sync/log', methods=['GET'])
@admin_required
@log_api_request
def get_sync_log():
    """Get QuickBooks sync log"""
    try:
        log = QuickBooksService.get_sync_log()
        return APIResponse.success(log, "Sync log retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve sync log: {str(e)}", status_code=500)


@quickbooks_bp.route('/synced-items', methods=['GET'])
@admin_required
@log_api_request
def get_synced_items():
    """Get items that have been synced with QuickBooks"""
    try:
        items = QuickBooksService.get_synced_items()
        return APIResponse.success(items, "Synced items retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve synced items: {str(e)}", status_code=500)
