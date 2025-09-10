"""
API Utilities

Provides standardized API response formatting, error handling, and validation utilities.
"""

from flask import jsonify, request
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback
import logging

class APIResponse:
    """Standardized API response class"""

    @staticmethod
    def success(data: Any = None, message: str = "Operation completed successfully",
                status_code: int = 200) -> tuple:
        """Create a successful API response"""
        response = {
            'success': True,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        return jsonify(response), status_code

    @staticmethod
    def error(message: str, error_code: str = None, status_code: int = 400,
              details: Any = None) -> tuple:
        """Create an error API response"""
        response = {
            'success': False,
            'error': message,
            'error_code': error_code,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details
        }
        return jsonify(response), status_code

    @staticmethod
    def validation_error(errors: List[str], status_code: int = 422) -> tuple:
        """Create a validation error response"""
        response = {
            'success': False,
            'error': 'Validation failed',
            'error_code': 'VALIDATION_ERROR',
            'timestamp': datetime.utcnow().isoformat(),
            'validation_errors': errors
        }
        return jsonify(response), status_code

    @staticmethod
    def not_found(resource: str = "Resource", status_code: int = 404) -> tuple:
        """Create a not found response"""
        response = {
            'success': False,
            'error': f'{resource} not found',
            'error_code': 'NOT_FOUND',
            'timestamp': datetime.utcnow().isoformat()
        }
        return jsonify(response), status_code

    @staticmethod
    def unauthorized(message: str = "Unauthorized access", status_code: int = 401) -> tuple:
        """Create an unauthorized response"""
        response = {
            'success': False,
            'error': message,
            'error_code': 'UNAUTHORIZED',
            'timestamp': datetime.utcnow().isoformat()
        }
        return jsonify(response), status_code

    @staticmethod
    def forbidden(message: str = "Access forbidden", status_code: int = 403) -> tuple:
        """Create a forbidden response"""
        response = {
            'success': False,
            'error': message,
            'error_code': 'FORBIDDEN',
            'timestamp': datetime.utcnow().isoformat()
        }
        return jsonify(response), status_code

    @staticmethod
    def server_error(message: str = "Internal server error", status_code: int = 500) -> tuple:
        """Create a server error response"""
        response = {
            'success': False,
            'error': message,
            'error_code': 'SERVER_ERROR',
            'timestamp': datetime.utcnow().isoformat()
        }
        return jsonify(response), status_code

def handle_api_error(func):
    """Decorator to handle API errors consistently"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logging.error(f"Validation error in {func.__name__}: {str(e)}")
            return APIResponse.error(str(e), 'VALIDATION_ERROR', 400)
        except PermissionError as e:
            logging.error(f"Permission error in {func.__name__}: {str(e)}")
            return APIResponse.forbidden(str(e))
        except FileNotFoundError as e:
            logging.error(f"Resource not found in {func.__name__}: {str(e)}")
            return APIResponse.not_found(str(e))
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {str(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            return APIResponse.server_error("An unexpected error occurred")
    return wrapper

def validate_required_fields(data: Dict, required_fields: List[str]) -> List[str]:
    """Validate that required fields are present in the data"""
    errors = []

    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            errors.append(f"Field '{field}' is required")

    return errors

def validate_request_data(required_fields: List[str] = None,
                         optional_fields: List[str] = None) -> Dict:
    """Validate request data and return validated data or raise error"""
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Request data is required")

        errors = []

        # Validate required fields
        if required_fields:
            errors.extend(validate_required_fields(data, required_fields))

        # Check for unknown fields
        if optional_fields:
            allowed_fields = set(required_fields or []) | set(optional_fields)
            unknown_fields = set(data.keys()) - allowed_fields
            if unknown_fields:
                errors.append(f"Unknown fields: {', '.join(unknown_fields)}")

        if errors:
            raise ValueError(f"Validation errors: {'; '.join(errors)}")

        return data

    except Exception as e:
        raise ValueError(f"Invalid request data: {str(e)}")

def paginate_results(query, page: int = 1, per_page: int = 20, max_per_page: int = 100):
    """Paginate query results"""
    try:
        # Validate pagination parameters
        page = max(1, int(page))
        per_page = min(max(1, int(per_page)), max_per_page)

        # Calculate offset
        offset = (page - 1) * per_page

        # Get total count
        total = query.count()

        # Get paginated results
        items = query.offset(offset).limit(per_page).all()

        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1

        return {
            'items': items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev,
                'next_page': page + 1 if has_next else None,
                'prev_page': page - 1 if has_prev else None
            }
        }

    except Exception as e:
        raise ValueError(f"Pagination error: {str(e)}")

def format_paginated_response(items: List[Any], pagination: Dict,
                            item_formatter: callable = None) -> Dict:
    """Format paginated response"""
    try:
        # Format items if formatter provided
        if item_formatter:
            formatted_items = [item_formatter(item) for item in items]
        else:
            formatted_items = items

        return {
            'success': True,
            'data': formatted_items,
            'pagination': pagination,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise ValueError(f"Response formatting error: {str(e)}")

def log_api_request(func):
    """Decorator to log API requests"""
    def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()

        # Log request
        logging.info(f"API Request: {request.method} {request.path}")
        logging.info(f"Request data: {request.get_json() if request.is_json else request.form}")

        try:
            result = func(*args, **kwargs)

            # Log successful response
            duration = (datetime.utcnow() - start_time).total_seconds()
            logging.info(f"API Response: {request.method} {request.path} - Success ({duration:.3f}s)")

            return result

        except Exception as e:
            # Log error response
            duration = (datetime.utcnow() - start_time).total_seconds()
            logging.error(f"API Error: {request.method} {request.path} - {str(e)} ({duration:.3f}s)")
            raise

    return wrapper

def rate_limit_check(limit: int = 100, window: int = 3600):
    """Simple rate limiting check (in-memory, not production-ready)"""
    # This is a simple implementation for demonstration
    # In production, use Redis or a proper rate limiting solution
    from flask import g

    if not hasattr(g, 'rate_limit_requests'):
        g.rate_limit_requests = []

    now = datetime.utcnow()

    # Remove old requests outside the window
    g.rate_limit_requests = [
        req_time for req_time in g.rate_limit_requests
        if (now - req_time).total_seconds() < window
    ]

    # Check if limit exceeded
    if len(g.rate_limit_requests) >= limit:
        return False

    # Add current request
    g.rate_limit_requests.append(now)
    return True

def require_api_key(api_key: str = None):
    """Decorator to require API key authentication"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Check for API key in headers
            provided_key = request.headers.get('X-API-Key')

            if not provided_key:
                return APIResponse.unauthorized("API key required")

            if api_key and provided_key != api_key:
                return APIResponse.unauthorized("Invalid API key")

            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_json_schema(schema: Dict):
    """Decorator to validate JSON schema"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json()
                if not data:
                    return APIResponse.error("JSON data required", 'INVALID_JSON', 400)

                # Simple schema validation (in production, use jsonschema library)
                errors = validate_against_schema(data, schema)
                if errors:
                    return APIResponse.validation_error(errors)

                return func(*args, **kwargs)

            except Exception as e:
                return APIResponse.error(f"Schema validation error: {str(e)}", 'SCHEMA_ERROR', 400)
        return wrapper
    return decorator

def validate_against_schema(data: Dict, schema: Dict) -> List[str]:
    """Simple schema validation (basic implementation)"""
    errors = []

    for field, rules in schema.items():
        if 'required' in rules and rules['required']:
            if field not in data or data[field] is None:
                errors.append(f"Field '{field}' is required")
                continue

        if field in data:
            value = data[field]

            # Type validation
            if 'type' in rules:
                expected_type = rules['type']
                if expected_type == 'string' and not isinstance(value, str):
                    errors.append(f"Field '{field}' must be a string")
                elif expected_type == 'integer' and not isinstance(value, int):
                    errors.append(f"Field '{field}' must be an integer")
                elif expected_type == 'number' and not isinstance(value, (int, float)):
                    errors.append(f"Field '{field}' must be a number")
                elif expected_type == 'boolean' and not isinstance(value, bool):
                    errors.append(f"Field '{field}' must be a boolean")

            # Length validation for strings
            if isinstance(value, str) and 'min_length' in rules:
                if len(value) < rules['min_length']:
                    errors.append(f"Field '{field}' must be at least {rules['min_length']} characters")

            if isinstance(value, str) and 'max_length' in rules:
                if len(value) > rules['max_length']:
                    errors.append(f"Field '{field}' must be at most {rules['max_length']} characters")

            # Range validation for numbers
            if isinstance(value, (int, float)) and 'min' in rules:
                if value < rules['min']:
                    errors.append(f"Field '{field}' must be at least {rules['min']}")

            if isinstance(value, (int, float)) and 'max' in rules:
                if value > rules['max']:
                    errors.append(f"Field '{field}' must be at most {rules['max']}")

    return errors
