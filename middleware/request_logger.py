"""
Request Logger Middleware

Provides comprehensive request logging for the Flask application.
"""

import time
import json

class RequestLogger:
    """Request logging middleware for the application"""

    @staticmethod
    def register_request_logging(app):
        """Register request logging middleware with the Flask application"""
        from flask import request, g
        from utils.logging_utils import log_api_request, log_system_event

        @app.before_request
        def log_request_start():
            """Log request start"""
            g.start_time = time.time()
            g.request_id = str(int(time.time() * 1000))  # Simple request ID

            # Log request details
            log_system_event("Request started", "info",
                           request_id=g.request_id,
                           method=request.method,
                           path=request.path,
                           remote_addr=request.remote_addr,
                           user_agent=request.headers.get('User-Agent', 'Unknown'))

        @app.after_request
        def log_request_end(response):
            """Log request completion"""
            if hasattr(g, 'start_time'):
                duration = time.time() - g.start_time

                # Safely get response size (skip for static files in passthrough mode)
                response_size = None
                try:
                    response_size = len(response.get_data())
                except RuntimeError:
                    # Static files are in direct passthrough mode, can't get size
                    response_size = "passthrough"

                # Log request completion
                log_system_event("Request completed", "info",
                               request_id=getattr(g, 'request_id', 'unknown'),
                               method=request.method,
                               path=request.path,
                               status_code=response.status_code,
                               duration=duration,
                               response_size=response_size)

                # Log slow requests
                if duration > 5.0:  # 5 seconds
                    log_system_event("Slow request detected", "warning",
                                   request_id=getattr(g, 'request_id', 'unknown'),
                                   method=request.method,
                                   path=request.path,
                                   duration=duration)

            return response

        @app.before_request
        def log_api_requests():
            """Log API requests with detailed information"""
            if request.path.startswith('/api/'):
                # Log API request details
                request_data = None
                if request.is_json:
                    try:
                        request_data = request.get_json()
                    except Exception:
                        request_data = "Invalid JSON"
                elif request.form:
                    request_data = dict(request.form)

                log_system_event("API request", "info",
                               method=request.method,
                               path=request.path,
                               query_params=dict(request.args),
                               request_data=request_data,
                               content_type=request.content_type,
                               remote_addr=request.remote_addr)

        @app.after_request
        def log_api_responses(response):
            """Log API responses with detailed information"""
            if request.path.startswith('/api/'):
                # Log API response details
                response_data = None
                if response.is_json:
                    try:
                        response_data = response.get_json()
                    except Exception:
                        response_data = "Invalid JSON"

                log_system_event("API response", "info",
                               method=request.method,
                               path=request.path,
                               status_code=response.status_code,
                               response_data=response_data,
                               content_type=response.content_type)

            return response

        @app.before_request
        def log_admin_requests():
            """Log admin requests for security monitoring"""
            if request.path.startswith('/admin/'):
                log_system_event("Admin request", "info",
                               method=request.method,
                               path=request.path,
                               remote_addr=request.remote_addr,
                               user_agent=request.headers.get('User-Agent', 'Unknown'),
                               referrer=request.headers.get('Referer', 'Direct'))

        @app.before_request
        def log_authentication_attempts():
            """Log authentication attempts"""
            if request.path in ['/admin/login', '/api/auth/login']:
                log_system_event("Authentication attempt", "info",
                               method=request.method,
                               path=request.path,
                               remote_addr=request.remote_addr,
                               user_agent=request.headers.get('User-Agent', 'Unknown'))

        @app.before_request
        def log_file_uploads():
            """Log file upload attempts"""
            if request.files:
                files_info = []
                for key, file in request.files.items():
                    files_info.append({
                        'field_name': key,
                        'filename': file.filename,
                        'content_type': file.content_type,
                        'size': len(file.read()) if file else 0
                    })
                    file.seek(0)  # Reset file pointer

                log_system_event("File upload attempt", "info",
                               method=request.method,
                               path=request.path,
                               files=files_info,
                               remote_addr=request.remote_addr)

        @app.before_request
        def log_database_operations():
            """Log database operations (placeholder for future implementation)"""
            # This would be implemented with SQLAlchemy event listeners
            pass

        @app.before_request
        def log_external_api_calls():
            """Log external API calls (placeholder for future implementation)"""
            # This would be implemented with request hooks for external APIs
            pass
