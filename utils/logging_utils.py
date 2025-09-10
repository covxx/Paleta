"""
Logging Utilities

Provides centralized logging configuration and utilities for the application.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, g

def setup_logging(app=None, log_level: str = 'INFO', log_file: str = None):
    """Setup application logging configuration"""

    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set default log file if not provided
    if not log_file:
        log_file = os.path.join(log_dir, 'app.log')

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)

    # Error file handler
    error_file = os.path.join(log_dir, 'error.log')
    error_handler = logging.handlers.RotatingFileHandler(
        error_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)

    # API request handler
    api_file = os.path.join(log_dir, 'api.log')
    api_handler = logging.handlers.RotatingFileHandler(
        api_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(detailed_formatter)

    # Create API logger
    api_logger = logging.getLogger('api')
    api_logger.addHandler(api_handler)
    api_logger.setLevel(logging.INFO)
    api_logger.propagate = False

    # Database handler
    db_file = os.path.join(log_dir, 'database.log')
    db_handler = logging.handlers.RotatingFileHandler(
        db_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    db_handler.setLevel(logging.INFO)
    db_handler.setFormatter(detailed_formatter)

    # Create database logger
    db_logger = logging.getLogger('database')
    db_logger.addHandler(db_handler)
    db_logger.setLevel(logging.INFO)
    db_logger.propagate = False

    # QuickBooks handler
    qb_file = os.path.join(log_dir, 'quickbooks.log')
    qb_handler = logging.handlers.RotatingFileHandler(
        qb_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    qb_handler.setLevel(logging.INFO)
    qb_handler.setFormatter(detailed_formatter)

    # Create QuickBooks logger
    qb_logger = logging.getLogger('quickbooks')
    qb_logger.addHandler(qb_handler)
    qb_logger.setLevel(logging.INFO)
    qb_logger.propagate = False

    # Printer handler
    printer_file = os.path.join(log_dir, 'printer.log')
    printer_handler = logging.handlers.RotatingFileHandler(
        printer_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    printer_handler.setLevel(logging.INFO)
    printer_handler.setFormatter(detailed_formatter)

    # Create printer logger
    printer_logger = logging.getLogger('printer')
    printer_logger.addHandler(printer_handler)
    printer_logger.setLevel(logging.INFO)
    printer_logger.propagate = False

    # Configure Flask app logging if provided
    if app:
        app.logger.setLevel(getattr(logging, log_level.upper()))
        app.logger.addHandler(console_handler)
        app.logger.addHandler(file_handler)

    logging.info(f"Logging configured - Level: {log_level}, File: {log_file}")

def log_api_request(func):
    """Decorator to log API requests"""
    from functools import wraps
    import time
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Log successful request
            if hasattr(result, 'status_code'):
                log_api_call(
                    method=request.method if request else 'UNKNOWN',
                    endpoint=request.path if request else 'UNKNOWN',
                    status_code=result.status_code,
                    duration=duration
                )
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            
            # Log failed request
            log_api_call(
                method=request.method if request else 'UNKNOWN',
                endpoint=request.path if request else 'UNKNOWN',
                status_code=500,
                duration=duration,
                error=str(e)
            )
            raise
    
    return wrapper

def log_api_call(method: str, endpoint: str, status_code: int,
                duration: float, user_id: str = None, **kwargs):
    """Log API call details"""
    api_logger = logging.getLogger('api')

    log_data = {
        'method': method,
        'endpoint': endpoint,
        'status_code': status_code,
        'duration': duration,
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat(),
        'ip_address': request.remote_addr if request else None,
        'user_agent': request.headers.get('User-Agent') if request else None
    }

    # Add any additional data
    log_data.update(kwargs)

    # Log based on status code
    if status_code >= 500:
        api_logger.error(f"API Error: {method} {endpoint} - {status_code} ({duration:.3f}s)", extra=log_data)
    elif status_code >= 400:
        api_logger.warning(f"API Warning: {method} {endpoint} - {status_code} ({duration:.3f}s)", extra=log_data)
    else:
        api_logger.info(f"API Call: {method} {endpoint} - {status_code} ({duration:.3f}s)", extra=log_data)

def log_error(error: Exception, context: str = None, **kwargs):
    """Log error with context"""
    logger = logging.getLogger()

    error_data = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context,
        'timestamp': datetime.utcnow().isoformat(),
        'ip_address': request.remote_addr if request else None,
        'user_agent': request.headers.get('User-Agent') if request else None
    }

    # Add any additional data
    error_data.update(kwargs)

    logger.error(f"Error in {context}: {str(error)}", extra=error_data, exc_info=True)

def log_database_operation(operation: str, table: str, record_id: str = None,
                          duration: float = None, **kwargs):
    """Log database operations"""
    db_logger = logging.getLogger('database')

    log_data = {
        'operation': operation,
        'table': table,
        'record_id': record_id,
        'duration': duration,
        'timestamp': datetime.utcnow().isoformat()
    }

    # Add any additional data
    log_data.update(kwargs)

    db_logger.info(f"DB {operation}: {table}" + (f" (ID: {record_id})" if record_id else ""), extra=log_data)

def log_quickbooks_operation(operation: str, status: str, **kwargs):
    """Log QuickBooks operations"""
    qb_logger = logging.getLogger('quickbooks')

    log_data = {
        'operation': operation,
        'status': status,
        'timestamp': datetime.utcnow().isoformat()
    }

    # Add any additional data
    log_data.update(kwargs)

    if status == 'error':
        qb_logger.error(f"QB {operation}: {status}", extra=log_data)
    elif status == 'warning':
        qb_logger.warning(f"QB {operation}: {status}", extra=log_data)
    else:
        qb_logger.info(f"QB {operation}: {status}", extra=log_data)

def log_printer_operation(operation: str, printer_id: str, status: str, **kwargs):
    """Log printer operations"""
    printer_logger = logging.getLogger('printer')

    log_data = {
        'operation': operation,
        'printer_id': printer_id,
        'status': status,
        'timestamp': datetime.utcnow().isoformat()
    }

    # Add any additional data
    log_data.update(kwargs)

    if status == 'error':
        printer_logger.error(f"Printer {operation}: {printer_id} - {status}", extra=log_data)
    elif status == 'warning':
        printer_logger.warning(f"Printer {operation}: {printer_id} - {status}", extra=log_data)
    else:
        printer_logger.info(f"Printer {operation}: {printer_id} - {status}", extra=log_data)

def log_user_action(action: str, user_id: str = None, **kwargs):
    """Log user actions"""
    logger = logging.getLogger('user_actions')

    log_data = {
        'action': action,
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat(),
        'ip_address': request.remote_addr if request else None,
        'user_agent': request.headers.get('User-Agent') if request else None
    }

    # Add any additional data
    log_data.update(kwargs)

    logger.info(f"User Action: {action}" + (f" (User: {user_id})" if user_id else ""), extra=log_data)

def log_system_event(event: str, level: str = 'info', **kwargs):
    """Log system events"""
    logger = logging.getLogger()

    log_data = {
        'event': event,
        'level': level,
        'timestamp': datetime.utcnow().isoformat()
    }

    # Add any additional data
    log_data.update(kwargs)

    if level == 'error':
        logger.error(f"System Event: {event}", extra=log_data)
    elif level == 'warning':
        logger.warning(f"System Event: {event}", extra=log_data)
    else:
        logger.info(f"System Event: {event}", extra=log_data)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)

def log_performance(operation: str, duration: float, **kwargs):
    """Log performance metrics"""
    logger = logging.getLogger('performance')

    log_data = {
        'operation': operation,
        'duration': duration,
        'timestamp': datetime.utcnow().isoformat()
    }

    # Add any additional data
    log_data.update(kwargs)

    # Log based on duration
    if duration > 5.0:  # 5 seconds
        logger.warning(f"Slow Operation: {operation} - {duration:.3f}s", extra=log_data)
    elif duration > 1.0:  # 1 second
        logger.info(f"Operation: {operation} - {duration:.3f}s", extra=log_data)
    else:
        logger.debug(f"Fast Operation: {operation} - {duration:.3f}s", extra=log_data)

def log_security_event(event: str, severity: str = 'info', **kwargs):
    """Log security events"""
    security_logger = logging.getLogger('security')

    log_data = {
        'event': event,
        'severity': severity,
        'timestamp': datetime.utcnow().isoformat(),
        'ip_address': request.remote_addr if request else None,
        'user_agent': request.headers.get('User-Agent') if request else None
    }

    # Add any additional data
    log_data.update(kwargs)

    if severity == 'critical':
        security_logger.critical(f"Security Event: {event}", extra=log_data)
    elif severity == 'high':
        security_logger.error(f"Security Event: {event}", extra=log_data)
    elif severity == 'medium':
        security_logger.warning(f"Security Event: {event}", extra=log_data)
    else:
        security_logger.info(f"Security Event: {event}", extra=log_data)

def cleanup_old_logs(days: int = 30):
    """Clean up old log files"""
    import glob
    from datetime import datetime, timedelta

    log_dir = 'logs'
    cutoff_date = datetime.now() - timedelta(days=days)

    # Find old log files
    log_patterns = [
        os.path.join(log_dir, '*.log.*'),  # Rotated logs
        os.path.join(log_dir, '*.log'),    # Current logs
    ]

    deleted_count = 0
    for pattern in log_patterns:
        for log_file in glob.glob(pattern):
            try:
                # Check file modification time
                file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                if file_time < cutoff_date:
                    os.remove(log_file)
                    deleted_count += 1
                    logging.info(f"Deleted old log file: {log_file}")
            except Exception as e:
                logging.error(f"Failed to delete log file {log_file}: {e}")

    logging.info(f"Cleaned up {deleted_count} old log files")
    return deleted_count
