"""
Users API v1

Handles all user-related API endpoints with proper versioning and error handling.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from services.user_service import UserService
from utils.api_utils import APIResponse, handle_api_error, validate_request_data, log_api_request

users_bp = Blueprint('users_v1', __name__, url_prefix='/api/v1/users')

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if not session.get('admin_logged_in'):
            return APIResponse.unauthorized("Admin authentication required")
        return f(*args, **kwargs)
    return decorated_function

@users_bp.route('/active', methods=['GET'])
@admin_required
@log_api_request
def get_active_users():
    """Get currently active users"""
    try:
        users = UserService.get_active_users()
        return APIResponse.success(users, "Active users retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve active users: {str(e)}", status_code=500)

@users_bp.route('/admin', methods=['GET'])
@admin_required
@log_api_request
def get_admin_users():
    """Get all admin users"""
    try:
        users = UserService.get_all_admin_users()
        return APIResponse.success(users, "Admin users retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve admin users: {str(e)}", status_code=500)

@users_bp.route('/admin', methods=['POST'])
@admin_required
@log_api_request
def create_admin_user():
    """Create a new admin user"""
    try:
        data = validate_request_data(['email', 'password', 'name'])
        result = UserService.create_admin_user(data)
        return APIResponse.success(result, "Admin user created successfully", status_code=201)
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to create admin user: {str(e)}", status_code=500)

@users_bp.route('/admin/<int:user_id>', methods=['PUT'])
@admin_required
@log_api_request
def update_admin_user(user_id):
    """Update an admin user"""
    try:
        data = validate_request_data(optional_fields=['email', 'password', 'name'])
        result = UserService.update_admin_user(user_id, data)
        return APIResponse.success(result, "Admin user updated successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to update admin user: {str(e)}", status_code=500)

@users_bp.route('/admin/<int:user_id>', methods=['DELETE'])
@admin_required
@log_api_request
def delete_admin_user(user_id):
    """Delete an admin user"""
    try:
        result = UserService.delete_admin_user(user_id)
        return APIResponse.success(result, "Admin user deleted successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to delete admin user: {str(e)}", status_code=500)

@users_bp.route('/kick/<user_id>', methods=['POST'])
@admin_required
@log_api_request
def kick_user(user_id):
    """Kick a user by terminating their session"""
    try:
        result = UserService.kick_user(user_id)
        return APIResponse.success(result, "User session terminated successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to kick user: {str(e)}", status_code=500)

@users_bp.route('/statistics', methods=['GET'])
@admin_required
@log_api_request
def get_user_statistics():
    """Get user statistics"""
    try:
        stats = UserService.get_user_statistics()
        return APIResponse.success(stats, "User statistics retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to retrieve user statistics: {str(e)}", status_code=500)

@users_bp.route('/search', methods=['GET'])
@admin_required
@log_api_request
def search_users():
    """Search users by name or email"""
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return APIResponse.error("Search term is required", 'VALIDATION_ERROR', 400)

        users = UserService.search_users(search_term)
        return APIResponse.success(users, f"Search results for '{search_term}' retrieved successfully")
    except Exception as e:
        return APIResponse.error(f"Failed to search users: {str(e)}", status_code=500)

@users_bp.route('/change-password', methods=['POST'])
@admin_required
@log_api_request
def change_password():
    """Change user password"""
    try:
        data = validate_request_data(['user_id', 'old_password', 'new_password'])
        result = UserService.change_password(data['user_id'], data['old_password'], data['new_password'])
        return APIResponse.success(result, "Password changed successfully")
    except ValueError as e:
        return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        return APIResponse.error(f"Failed to change password: {str(e)}", status_code=500)
