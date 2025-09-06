# Configuration file for Inventory Management System

# Server Configuration
HOST = '0.0.0.0'  # Bind to all network interfaces for multi-PC access
PORT = 5002        # Port number for the web server
DEBUG = True       # Set to False for production use

# Database Configuration
DATABASE_URI = 'sqlite:///inventory.db'

# Security Configuration
SECRET_KEY = 'your-secret-key-here-change-this-in-production'

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

# Logging Configuration
LOG_LEVEL = 'INFO'   # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = 'inventory.log'

# CORS Configuration (for multi-PC access)
CORS_ORIGINS = ['*']  # Allow all origins for network access
