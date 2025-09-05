# Production Configuration for Ubuntu VPS
# Optimized for 4-core system with concurrent users

# Server Configuration
HOST = '127.0.0.1'  # Bind to localhost (Nginx will handle external access)
PORT = 8000         # Internal port for Gunicorn
DEBUG = False       # Disable debug mode for production

# Database Configuration - Optimized for concurrent access
DATABASE_URI = 'sqlite:///inventory.db'
# For high-traffic production, consider PostgreSQL:
# DATABASE_URI = 'postgresql://user:password@localhost/inventory'

# Security Configuration - CHANGE THESE IN PRODUCTION
SECRET_KEY = 'your-production-secret-key-change-this-immediately'

# Company Information (for labels)
COMPANY_NAME = "Palumbo Foods, LLC"
COMPANY_ADDRESS = "8794 Gap Newport Pike Avondale, PA 19311"

# Label Configuration
LABEL_WIDTH = 4.0    # Label width in inches (4 inches)
LABEL_HEIGHT = 2.0   # Label height in inches (2 inches)
LABEL_MARGIN = 0.1   # Label margin in inches (tight margins for 4x2)

# LOT Code Configuration
LOT_PREFIX = 'LOT'   # Prefix for LOT codes
LOT_TIMESTAMP_FORMAT = '%Y%m%d%H%M'  # Timestamp format in LOT codes
LOT_RANDOM_SUFFIX_LENGTH = 4  # Length of random suffix

# QR Code Configuration
QR_VERSION = 1       # QR code version (1-40)
QR_BOX_SIZE = 2     # QR code box size
QR_BORDER = 1       # QR code border width

# File Paths
TEMPLATES_FOLDER = 'templates'
STATIC_FOLDER = 'static'
UPLOAD_FOLDER = 'uploads'

# Production Logging Configuration
LOG_LEVEL = 'WARNING'   # Reduce log verbosity in production
LOG_FILE = '/var/log/label-printer/app.log'
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# CORS Configuration (restrict for production)
CORS_ORIGINS = ['https://yourdomain.com']  # Replace with your actual domain

# Performance Configuration
MAX_WORKERS = 4  # Match your VPS core count
WORKER_TIMEOUT = 120  # 2 minutes
WORKER_CONNECTIONS = 1000
KEEPALIVE = 2

# Database Connection Pool Settings (optimized for 4 cores)
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_TIMEOUT = 30
DB_POOL_RECYCLE = 3600  # 1 hour

# Cache Configuration
CACHE_TYPE = 'redis'  # Use Redis for production caching
CACHE_REDIS_URL = 'redis://localhost:6379/0'
CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes

# Rate Limiting (more restrictive for production)
RATE_LIMIT_REQUESTS = 100  # requests per minute
RATE_LIMIT_WINDOW = 60     # seconds

# File Upload Limits
MAX_FILE_SIZE = 8 * 1024 * 1024  # 8MB max file size (reduced for production)

# Security Headers
SECURE_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
}
