"""
API Blueprint Registration

Registers all API version blueprints with the Flask application.
"""

from flask import Flask
from api.v1 import (
    items_bp, lots_bp, orders_bp, customers_bp,
    printers_bp, users_bp, quickbooks_bp
)

def register_api_blueprints(app: Flask):
    """Register all API blueprints with the Flask application"""

    # Register v1 API blueprints
    app.register_blueprint(items_bp)
    app.register_blueprint(lots_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(printers_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(quickbooks_bp)

    # Add API health check endpoint
    @app.route('/api/health', methods=['GET'])
    def api_health():
        """API health check endpoint"""
        return {
            'status': 'healthy',
            'version': '1.0.0',
            'timestamp': '2025-01-10T10:00:00Z'
        }

    # Add API version info endpoint
    @app.route('/api/version', methods=['GET'])
    def api_version():
        """API version information"""
        return {
            'api_version': '1.0.0',
            'supported_versions': ['1.0.0'],
            'deprecated_versions': [],
            'endpoints': {
                'v1': {
                    'items': '/api/v1/items',
                    'lots': '/api/v1/lots',
                    'orders': '/api/v1/orders',
                    'customers': '/api/v1/customers',
                    'printers': '/api/v1/printers',
                    'users': '/api/v1/users',
                    'quickbooks': '/api/v1/quickbooks'
                }
            }
        }
