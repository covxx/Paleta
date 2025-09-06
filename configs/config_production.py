# Production Configuration for QuickBooks Label Printer
# This configuration is optimized for VPS deployment

import os
from datetime import timedelta

class ProductionConfig:
    """Production configuration for VPS deployment"""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-super-secret-production-key-change-this')
    
    # Database Configuration
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///instance/inventory.db')
    
    # Server Configuration
    HOST = '127.0.0.1'  # Bind to localhost only (Nginx will proxy)
    PORT = 5002
    DEBUG = False  # Never enable debug in production
    
    # SQLAlchemy Configuration for Production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0,
        'pool_size': 10,  # Increased for production
        'echo': False,    # Disable SQL logging in production
    }
    
    # QuickBooks API Configuration
    QB_CLIENT_ID = os.environ.get('QB_CLIENT_ID', 'ABUW0U3AsMTGyq7bb1ujpj17IodZlrGkMYtjaWGfke6gcztmtY')
    QB_CLIENT_SECRET = os.environ.get('QB_CLIENT_SECRET', 'H75cxmzTruVA2LpU27IyAUzJKJlsNgWHMrJaz3MN')
    QB_COMPANY_ID = os.environ.get('QB_COMPANY_ID', '9341455300640805')
    QB_SANDBOX = os.environ.get('QB_SANDBOX', 'true').lower() == 'true'
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File Upload Configuration
    UPLOAD_FOLDER = '/opt/label-printer/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/opt/label-printer/logs/app.log'
    
    # Performance Configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Frame-Options': 'SAMEORIGIN',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    }
    
    # Email Configuration (for notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@yourdomain.com')
    
    # Monitoring Configuration
    ENABLE_METRICS = True
    METRICS_ENDPOINT = '/metrics'
    
    # Backup Configuration
    BACKUP_ENABLED = True
    BACKUP_SCHEDULE = '0 2 * * *'  # Daily at 2 AM
    BACKUP_RETENTION_DAYS = 30
    
    # Auto-sync Configuration
    AUTO_SYNC_ENABLED = True
    AUTO_SYNC_INTERVAL = 60  # minutes
    AUTO_SYNC_TIMEOUT = 300  # seconds
    
    # Error Handling
    ERROR_EMAIL_RECIPIENTS = os.environ.get('ERROR_EMAIL_RECIPIENTS', '').split(',')
    SEND_ERROR_EMAILS = bool(ERROR_EMAIL_RECIPIENTS and ERROR_EMAIL_RECIPIENTS[0])
    
    # Database Backup
    DB_BACKUP_ENABLED = True
    DB_BACKUP_SCHEDULE = '0 3 * * *'  # Daily at 3 AM
    DB_BACKUP_RETENTION_DAYS = 7
    
    # Performance Monitoring
    ENABLE_PROFILING = False  # Only enable for debugging
    PROFILING_SAMPLE_RATE = 0.1  # 10% of requests
    
    # Cache Configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    USE_REDIS_CACHE = os.environ.get('USE_REDIS_CACHE', 'false').lower() == 'true'
    
    # SSL Configuration
    SSL_REDIRECT = True
    FORCE_HTTPS = True
    
    # API Configuration
    API_RATE_LIMIT = "1000 per hour"
    API_TIMEOUT = 30  # seconds
    
    # File Storage
    USE_S3 = os.environ.get('USE_S3', 'false').lower() == 'true'
    S3_BUCKET = os.environ.get('S3_BUCKET', '')
    S3_REGION = os.environ.get('S3_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    
    # Health Check Configuration
    HEALTH_CHECK_ENABLED = True
    HEALTH_CHECK_ENDPOINT = '/health'
    HEALTH_CHECK_TIMEOUT = 5  # seconds
    
    # Maintenance Mode
    MAINTENANCE_MODE = False
    MAINTENANCE_MESSAGE = "System is under maintenance. Please try again later."
    
    # Feature Flags
    FEATURES = {
        'quickbooks_integration': True,
        'auto_sync': True,
        'backup': True,
        'monitoring': True,
        'email_notifications': True,
        'api_access': True,
        'admin_interface': True,
        'label_designer': True,
        'order_management': True,
        'inventory_management': True,
        'customer_management': True,
        'reporting': True,
        'bulk_operations': True,
        'export_functionality': True,
        'import_functionality': True
    }
    
    # Performance Tuning
    WORKER_PROCESSES = 4  # Match VPS cores
    WORKER_CONNECTIONS = 1000
    WORKER_TIMEOUT = 30
    KEEPALIVE_TIMEOUT = 2
    MAX_REQUESTS = 1000
    MAX_REQUESTS_JITTER = 100
    
    # Database Connection Pool
    DB_POOL_SIZE = 10
    DB_POOL_OVERFLOW = 20
    DB_POOL_TIMEOUT = 30
    DB_POOL_RECYCLE = 3600
    
    # Session Store
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = '/opt/label-printer/sessions'
    SESSION_FILE_THRESHOLD = 500
    
    # Logging
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Error Pages
    ERROR_PAGES = {
        404: 'errors/404.html',
        500: 'errors/500.html',
        403: 'errors/403.html'
    }
    
    # API Documentation
    API_DOCS_ENABLED = True
    API_DOCS_URL = '/api/docs'
    
    # Webhook Configuration
    WEBHOOK_ENABLED = True
    WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')
    WEBHOOK_TIMEOUT = 10  # seconds
    
    # Notification Configuration
    NOTIFICATIONS = {
        'email': True,
        'webhook': True,
        'slack': False,
        'discord': False
    }
    
    # Slack Configuration (if enabled)
    SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL', '')
    SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', '#alerts')
    
    # Discord Configuration (if enabled)
    DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')
    
    # Analytics
    ANALYTICS_ENABLED = False
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', '')
    
    # CDN Configuration
    CDN_ENABLED = False
    CDN_URL = os.environ.get('CDN_URL', '')
    
    # Compression
    COMPRESS_ENABLED = True
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500
    
    # Static Files
    STATIC_URL_PATH = '/static'
    STATIC_FOLDER = 'static'
    
    # Template Configuration
    TEMPLATES_AUTO_RELOAD = False  # Disable in production
    
    # JSON Configuration
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # Request Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_HEADERS = ['Content-Type', 'Authorization']
    
    # Security Configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # Password Configuration
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SYMBOLS = True
    
    # Session Security
    SESSION_COOKIE_NAME = 'label_printer_session'
    SESSION_COOKIE_DOMAIN = None
    SESSION_COOKIE_PATH = '/'
    SESSION_COOKIE_MAX_AGE = 28800  # 8 hours
    
    # Remember Me Configuration
    REMEMBER_COOKIE_NAME = 'label_printer_remember'
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    
    # Admin Configuration
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@yourdomain.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')
    
    # QuickBooks Configuration
    QB_REDIRECT_URI = os.environ.get('QB_REDIRECT_URI', 'https://yourdomain.com/oauth-callback')
    QB_SCOPE = 'com.intuit.quickbooks.accounting'
    QB_TOKEN_EXPIRY_BUFFER = 300  # 5 minutes
    
    # Sync Configuration
    SYNC_BATCH_SIZE = 100
    SYNC_RETRY_ATTEMPTS = 3
    SYNC_RETRY_DELAY = 5  # seconds
    SYNC_TIMEOUT = 300  # 5 minutes
    
    # File Processing
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'csv', 'xlsx'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    # Database Migrations
    MIGRATION_DIR = 'migrations'
    MIGRATION_AUTO = False  # Manual migrations in production
    
    # Testing
    TESTING = False
    WTF_CSRF_ENABLED = True
    
    # Development
    DEVELOPMENT = False
    
    # Production
    PRODUCTION = True