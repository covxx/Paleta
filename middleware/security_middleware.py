"""
Security Middleware

Provides security features and monitoring for the Flask application.
"""

from flask import Flask, request, session, g
from utils.logging_utils import log_security_event, log_system_event
import time
import hashlib
from datetime import datetime, timedelta


class SecurityMiddleware:
    """Security middleware for the application"""
    
    def __init__(self):
        self.failed_attempts = {}  # Track failed login attempts
        self.rate_limit_requests = {}  # Track rate limiting
        self.suspicious_ips = set()  # Track suspicious IPs
    
    def register_security_middleware(self, app: Flask):
        """Register security middleware with the Flask application"""
        
        @app.before_request
        def check_rate_limiting():
            """Check rate limiting for requests"""
            client_ip = request.remote_addr
            current_time = time.time()
            
            # Clean old entries (older than 1 hour)
            cutoff_time = current_time - 3600
            if client_ip in self.rate_limit_requests:
                self.rate_limit_requests[client_ip] = [
                    req_time for req_time in self.rate_limit_requests[client_ip]
                    if req_time > cutoff_time
                ]
            
            # Check rate limit (100 requests per hour)
            if client_ip in self.rate_limit_requests:
                if len(self.rate_limit_requests[client_ip]) >= 100:
                    log_security_event("Rate limit exceeded", "high",
                                     ip_address=client_ip,
                                     path=request.path,
                                     method=request.method)
                    return "Rate limit exceeded", 429
            
            # Add current request
            if client_ip not in self.rate_limit_requests:
                self.rate_limit_requests[client_ip] = []
            self.rate_limit_requests[client_ip].append(current_time)
        
        @app.before_request
        def check_suspicious_activity():
            """Check for suspicious activity patterns"""
            client_ip = request.remote_addr
            
            # Check for multiple failed login attempts
            if client_ip in self.failed_attempts:
                failed_count = self.failed_attempts[client_ip]['count']
                last_attempt = self.failed_attempts[client_ip]['last_attempt']
                
                # If more than 5 failed attempts in last 15 minutes
                if failed_count >= 5 and time.time() - last_attempt < 900:
                    if client_ip not in self.suspicious_ips:
                        self.suspicious_ips.add(client_ip)
                        log_security_event("Suspicious IP detected", "high",
                                         ip_address=client_ip,
                                         failed_attempts=failed_count,
                                         reason="Multiple failed login attempts")
            
            # Block suspicious IPs
            if client_ip in self.suspicious_ips:
                log_security_event("Blocked suspicious IP", "high",
                                 ip_address=client_ip,
                                 path=request.path,
                                 method=request.method)
                return "Access denied", 403
        
        @app.before_request
        def check_admin_access():
            """Check admin access and log admin activities"""
            if request.path.startswith('/admin/'):
                # Check if user is logged in as admin
                if not session.get('admin_logged_in'):
                    log_security_event("Unauthorized admin access attempt", "medium",
                                     ip_address=request.remote_addr,
                                     path=request.path,
                                     method=request.method,
                                     user_agent=request.headers.get('User-Agent', 'Unknown'))
                    return "Unauthorized", 401
                
                # Log admin activities
                log_security_event("Admin activity", "info",
                                 admin_email=session.get('admin_email', 'Unknown'),
                                 ip_address=request.remote_addr,
                                 path=request.path,
                                 method=request.method)
        
        @app.before_request
        def check_api_access():
            """Check API access and log API activities"""
            if request.path.startswith('/api/'):
                # Log API access
                log_security_event("API access", "info",
                                 ip_address=request.remote_addr,
                                 path=request.path,
                                 method=request.method,
                                 user_agent=request.headers.get('User-Agent', 'Unknown'))
                
                # Check for admin-only API endpoints
                admin_endpoints = ['/api/admin-users', '/api/kick-user', '/api/quickbooks']
                if any(endpoint in request.path for endpoint in admin_endpoints):
                    if not session.get('admin_logged_in'):
                        log_security_event("Unauthorized API access attempt", "medium",
                                         ip_address=request.remote_addr,
                                         path=request.path,
                                         method=request.method)
                        return "Unauthorized", 401
        
        @app.before_request
        def check_file_upload_security():
            """Check file upload security"""
            if request.files:
                for key, file in request.files.items():
                    if file and file.filename:
                        # Check file extension
                        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.csv'}
                        file_ext = '.' + file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                        
                        if file_ext not in allowed_extensions:
                            log_security_event("Blocked file upload attempt", "medium",
                                             ip_address=request.remote_addr,
                                             filename=file.filename,
                                             file_extension=file_ext,
                                             path=request.path)
                            return "File type not allowed", 400
                        
                        # Check file size (10MB limit)
                        file.seek(0, 2)  # Seek to end
                        file_size = file.tell()
                        file.seek(0)  # Reset to beginning
                        
                        if file_size > 10 * 1024 * 1024:  # 10MB
                            log_security_event("Blocked large file upload", "medium",
                                             ip_address=request.remote_addr,
                                             filename=file.filename,
                                             file_size=file_size,
                                             path=request.path)
                            return "File too large", 400
        
        @app.before_request
        def check_sql_injection():
            """Basic SQL injection detection"""
            # Check query parameters for suspicious patterns
            suspicious_patterns = ['union', 'select', 'insert', 'update', 'delete', 'drop', 'create', 'alter']
            
            for key, value in request.args.items():
                if isinstance(value, str):
                    value_lower = value.lower()
                    for pattern in suspicious_patterns:
                        if pattern in value_lower:
                            log_security_event("Potential SQL injection attempt", "high",
                                             ip_address=request.remote_addr,
                                             parameter=key,
                                             value=value,
                                             path=request.path)
                            return "Invalid request", 400
        
        @app.before_request
        def check_xss():
            """Basic XSS detection"""
            # Check for script tags in request data
            xss_patterns = ['<script', 'javascript:', 'onload=', 'onerror=']
            
            # Check query parameters
            for key, value in request.args.items():
                if isinstance(value, str):
                    value_lower = value.lower()
                    for pattern in xss_patterns:
                        if pattern in value_lower:
                            log_security_event("Potential XSS attempt", "high",
                                             ip_address=request.remote_addr,
                                             parameter=key,
                                             value=value,
                                             path=request.path)
                            return "Invalid request", 400
        
        @app.before_request
        def log_session_activity():
            """Log session activity for security monitoring"""
            if session:
                session_id = session.get('_id', 'unknown')
                log_security_event("Session activity", "info",
                                 session_id=session_id,
                                 ip_address=request.remote_addr,
                                 path=request.path,
                                 method=request.method)
    
    def record_failed_login(self, ip_address: str):
        """Record a failed login attempt"""
        current_time = time.time()
        
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = {'count': 0, 'last_attempt': 0}
        
        self.failed_attempts[ip_address]['count'] += 1
        self.failed_attempts[ip_address]['last_attempt'] = current_time
        
        log_security_event("Failed login attempt", "medium",
                         ip_address=ip_address,
                         attempt_count=self.failed_attempts[ip_address]['count'])
    
    def clear_failed_attempts(self, ip_address: str):
        """Clear failed login attempts for an IP"""
        if ip_address in self.failed_attempts:
            del self.failed_attempts[ip_address]
    
    def is_ip_suspicious(self, ip_address: str) -> bool:
        """Check if an IP is marked as suspicious"""
        return ip_address in self.suspicious_ips
    
    def remove_suspicious_ip(self, ip_address: str):
        """Remove an IP from suspicious list"""
        self.suspicious_ips.discard(ip_address)
