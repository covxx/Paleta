"""
Error Handler Middleware

Provides centralized error handling for the Flask application.
"""

import traceback

class ErrorHandler:
    """Centralized error handling for the application"""

    @staticmethod
    def register_error_handlers(app):
        """Register error handlers with the Flask application"""
        from flask import request, jsonify, render_template
        from utils.logging_utils import log_error, log_system_event
        from utils.api_utils import APIResponse

        @app.errorhandler(400)
        def bad_request(error):
            """Handle 400 Bad Request errors"""
            log_error(error, "Bad Request",
                     path=request.path, method=request.method)

            if request.path.startswith('/api/'):
                return APIResponse.error("Bad Request", "BAD_REQUEST", 400)
            else:
                return render_template('error.html',
                                     error_code=400,
                                     error_message="Bad Request"), 400

        @app.errorhandler(401)
        def unauthorized(error):
            """Handle 401 Unauthorized errors"""
            log_error(error, "Unauthorized",
                     path=request.path, method=request.method)

            if request.path.startswith('/api/'):
                return APIResponse.unauthorized("Authentication required")
            else:
                return render_template('error.html',
                                     error_code=401,
                                     error_message="Authentication required"), 401

        @app.errorhandler(403)
        def forbidden(error):
            """Handle 403 Forbidden errors"""
            log_error(error, "Forbidden",
                     path=request.path, method=request.method)

            if request.path.startswith('/api/'):
                return APIResponse.forbidden("Access forbidden")
            else:
                return render_template('error.html',
                                     error_code=403,
                                     error_message="Access forbidden"), 403

        @app.errorhandler(404)
        def not_found(error):
            """Handle 404 Not Found errors"""
            log_error(error, "Not Found",
                     path=request.path, method=request.method)

            if request.path.startswith('/api/'):
                return APIResponse.not_found("Resource not found")
            else:
                return render_template('error.html',
                                     error_code=404,
                                     error_message="Page not found"), 404

        @app.errorhandler(405)
        def method_not_allowed(error):
            """Handle 405 Method Not Allowed errors"""
            log_error(error, "Method Not Allowed",
                     path=request.path, method=request.method)

            if request.path.startswith('/api/'):
                return APIResponse.error("Method not allowed", "METHOD_NOT_ALLOWED", 405)
            else:
                return render_template('error.html',
                                     error_code=405,
                                     error_message="Method not allowed"), 405

        @app.errorhandler(422)
        def unprocessable_entity(error):
            """Handle 422 Unprocessable Entity errors"""
            log_error(error, "Unprocessable Entity",
                     path=request.path, method=request.method)

            if request.path.startswith('/api/'):
                return APIResponse.error("Unprocessable entity", "UNPROCESSABLE_ENTITY", 422)
            else:
                return render_template('error.html',
                                     error_code=422,
                                     error_message="Unprocessable entity"), 422

        @app.errorhandler(429)
        def too_many_requests(error):
            """Handle 429 Too Many Requests errors"""
            log_error(error, "Too Many Requests",
                     path=request.path, method=request.method)

            if request.path.startswith('/api/'):
                return APIResponse.error("Too many requests", "RATE_LIMIT_EXCEEDED", 429)
            else:
                return render_template('error.html',
                                     error_code=429,
                                     error_message="Too many requests"), 429

        @app.errorhandler(500)
        def internal_server_error(error):
            """Handle 500 Internal Server Error"""
            log_error(error, "Internal Server Error",
                     path=request.path, method=request.method)

            if request.path.startswith('/api/'):
                return APIResponse.server_error("Internal server error")
            else:
                return render_template('error.html',
                                     error_code=500,
                                     error_message="Internal server error"), 500

        @app.errorhandler(502)
        def bad_gateway(error):
            """Handle 502 Bad Gateway errors"""
            log_error(error, "Bad Gateway",
                     path=request.path, method=request.method)

            if request.path.startswith('/api/'):
                return APIResponse.error("Bad gateway", "BAD_GATEWAY", 502)
            else:
                return render_template('error.html',
                                     error_code=502,
                                     error_message="Bad gateway"), 502

        @app.errorhandler(503)
        def service_unavailable(error):
            """Handle 503 Service Unavailable errors"""
            log_error(error, "Service Unavailable",
                     path=request.path, method=request.method)

            if request.path.startswith('/api/'):
                return APIResponse.error("Service unavailable", "SERVICE_UNAVAILABLE", 503)
            else:
                return render_template('error.html',
                                     error_code=503,
                                     error_message="Service unavailable"), 503

        @app.errorhandler(Exception)
        def handle_unexpected_error(error):
            """Handle unexpected errors"""
            log_error(error, "Unexpected Error",
                     path=request.path, method=request.method)

            # Log system event for critical errors
            log_system_event("Critical error occurred", "error",
                           error_type=type(error).__name__,
                           error_message=str(error))

            if request.path.startswith('/api/'):
                return APIResponse.server_error("An unexpected error occurred")
            else:
                return render_template('error.html',
                                     error_code=500,
                                     error_message="An unexpected error occurred"), 500
