# ProduceFlow Label Printer - Technical Documentation

## 📋 Table of Contents
1. [System Architecture](#system-architecture)
2. [Installation Guide](#installation-guide)
3. [Configuration](#configuration)
4. [API Reference](#api-reference)
5. [Database Schema](#database-schema)
6. [Deployment](#deployment)
7. [Monitoring](#monitoring)
8. [Security](#security)
9. [Development](#development)
10. [Troubleshooting](#troubleshooting)

---

## 🏗️ System Architecture

### Technology Stack
```
Frontend: HTML5, CSS3, JavaScript (Bootstrap 5)
Backend: Python 3.8+ with Flask
Database: SQLite 3.31+
Web Server: Nginx 1.18+
WSGI Server: Gunicorn 20.1+
Integration: QuickBooks Online API
Printing: ZPL (Zebra Programming Language)
```

### Component Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                             │
├─────────────────────────────────────────────────────────────┤
│  Web Browser  │  Mobile Browser  │  Admin Interface        │
└─────────────────┬─────────────────┬─────────────────────────┘
                  │                 │
┌─────────────────▼─────────────────▼─────────────────────────┐
│                    Web Layer                                │
├─────────────────────────────────────────────────────────────┤
│  Nginx (Reverse Proxy, SSL Termination, Static Files)      │
└─────────────────────────────────┬───────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────┐
│                Application Layer                            │
├─────────────────────────────────────────────────────────────┤
│  Flask Application (Gunicorn WSGI)                         │
│  ├── Routes & Controllers                                   │
│  ├── Business Logic                                         │
│  ├── Data Models                                            │
│  └── API Endpoints                                          │
└─────────────────────────────────┬───────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────┐
│                    Data Layer                               │
├─────────────────────────────────────────────────────────────┤
│  SQLite Database                                            │
│  ├── Items & Inventory                                      │
│  ├── Orders & Customers                                     │
│  ├── Printers & Configuration                               │
│  └── System Data                                            │
└─────────────────────────────────┬───────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────┐
│                Integration Layer                            │
├─────────────────────────────────────────────────────────────┤
│  QuickBooks Online API                                      │
│  ├── OAuth 2.0 Authentication                              │
│  ├── Customer Synchronization                               │
│  ├── Item Synchronization                                   │
│  └── Order Synchronization                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation Guide

### Prerequisites
```bash
# Ubuntu 20.04+ LTS
sudo apt update
sudo apt upgrade -y

# Required packages
sudo apt install -y python3 python3-pip python3-venv git nginx sqlite3
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
```

### Quick Installation
```bash
# One-command installation
curl -sSL https://raw.githubusercontent.com/covxx/Paleta/refs/heads/master/scripts/deploy_production.sh | sudo bash
```

### Manual Installation
```bash
# 1. Clone repository
git clone https://github.com/covxx/Paleta.git /opt/label-printer
cd /opt/label-printer

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python3 init_database_simple.py

# 5. Configure systemd service
sudo cp configs/label-printer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable label-printer

# 6. Configure Nginx
sudo cp configs/nginx.conf /etc/nginx/sites-available/label-printer
sudo ln -s /etc/nginx/sites-available/label-printer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 7. Start services
sudo systemctl start label-printer
sudo systemctl start nginx
```

---

## ⚙️ Configuration

### Environment Variables
```bash
# Application settings
export FLASK_ENV=production
export FLASK_DEBUG=False
export SECRET_KEY=your-secret-key-here

# Database settings
export DATABASE_URL=sqlite:///instance/inventory.db

# QuickBooks settings
export QB_CLIENT_ID=your-quickbooks-client-id
export QB_CLIENT_SECRET=your-quickbooks-client-secret
export QB_REDIRECT_URI=https://app.srjlabs.dev/qb/callback
export QB_SCOPE=com.intuit.quickbooks.accounting

# Printer settings
export DEFAULT_PRINTER_IP=192.168.1.100
export DEFAULT_PRINTER_PORT=9100
```

### Application Configuration
```python
# config.py
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/inventory.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # QuickBooks Configuration
    QB_CLIENT_ID = os.environ.get('QB_CLIENT_ID')
    QB_CLIENT_SECRET = os.environ.get('QB_CLIENT_SECRET')
    QB_REDIRECT_URI = os.environ.get('QB_REDIRECT_URI')
    QB_SCOPE = os.environ.get('QB_SCOPE')
    
    # Printer Configuration
    DEFAULT_PRINTER_IP = os.environ.get('DEFAULT_PRINTER_IP', '192.168.1.100')
    DEFAULT_PRINTER_PORT = int(os.environ.get('DEFAULT_PRINTER_PORT', 9100))
```

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/label-printer
server {
    listen 80;
    server_name app.srjlabs.dev;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.srjlabs.dev;
    
    ssl_certificate /etc/letsencrypt/live/app.srjlabs.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.srjlabs.dev/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /opt/label-printer/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Systemd Service
```ini
# /etc/systemd/system/label-printer.service
[Unit]
Description=ProduceFlow Label Printer
After=network.target

[Service]
Type=exec
User=labelprinter
Group=labelprinter
WorkingDirectory=/opt/label-printer
ExecStart=/usr/bin/python3 -m gunicorn --bind 127.0.0.1:5002 --workers 1 --timeout 60 --log-level info app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 🔌 API Reference

### Authentication
All admin endpoints require authentication via session or API key.

### Core Endpoints

#### Items API
```http
GET /api/items
POST /api/items
PUT /api/items/<id>
DELETE /api/items/<id>
```

**Item Object:**
```json
{
  "id": 1,
  "name": "Organic Apples",
  "item_code": "APP001",
  "gtin": "1234567890123",
  "category": "Produce",
  "description": "Fresh organic apples",
  "unit_price": 2.99,
  "quickbooks_id": "QB_APP001",
  "created_at": "2025-01-09T10:00:00Z",
  "updated_at": "2025-01-09T10:00:00Z"
}
```

#### LOTs API
```http
GET /api/lots
POST /api/lots
PUT /api/lots/<id>
DELETE /api/lots/<id>
```

**LOT Object:**
```json
{
  "id": 1,
  "lot_code": "LOT-20250109-001",
  "item_id": 1,
  "quantity": 100,
  "unit": "pcs",
  "expiry_date": "2025-01-16",
  "vendor_id": 1,
  "status": "active",
  "created_at": "2025-01-09T10:00:00Z"
}
```

#### Orders API
```http
GET /api/orders
POST /api/orders
PUT /api/orders/<id>
DELETE /api/orders/<id>
```

**Order Object:**
```json
{
  "id": 1,
  "order_number": "ORD-20250109-001",
  "customer_id": 1,
  "status": "pending",
  "total_amount": 299.00,
  "created_at": "2025-01-09T10:00:00Z",
  "quickbooks_synced": false
}
```

#### Printers API
```http
GET /api/printers
POST /api/printers
PUT /api/printers/<id>
DELETE /api/printers/<id>
POST /api/printers/<id>/test
```

**Printer Object:**
```json
{
  "id": 1,
  "name": "Zebra ZD420",
  "ip_address": "192.168.1.100",
  "port": 9100,
  "printer_type": "zebra",
  "label_width": 4.0,
  "label_height": 2.0,
  "dpi": 203,
  "status": "online",
  "last_seen": "2025-01-09T10:00:00Z"
}
```

### QuickBooks API

#### Connection Management
```http
GET /api/quickbooks/status
POST /api/quickbooks/connect
POST /api/quickbooks/disconnect
POST /api/quickbooks/test-connection
```

#### Data Synchronization
```http
POST /api/quickbooks/sync/items
POST /api/quickbooks/sync/customers
POST /api/quickbooks/sync/orders
GET /api/quickbooks/synced-items
GET /api/quickbooks/sync/log
GET /api/quickbooks/sync/statistics
```

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2025-01-09T10:00:00Z"
}
```

### Error Format
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2025-01-09T10:00:00Z"
}
```

---

## 🗄️ Database Schema

### Core Tables

#### Items Table
```sql
CREATE TABLE item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    item_code VARCHAR(50) UNIQUE,
    gtin VARCHAR(20),
    category VARCHAR(50),
    description TEXT,
    unit_price DECIMAL(10,2),
    quickbooks_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_item_name ON item(name);
CREATE INDEX idx_item_code ON item(item_code);
CREATE INDEX idx_item_gtin ON item(gtin);
```

#### LOTs Table
```sql
CREATE TABLE lot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_code VARCHAR(50) UNIQUE NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit VARCHAR(20) DEFAULT 'pcs',
    expiry_date DATE,
    vendor_id INTEGER,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES item(id),
    FOREIGN KEY (vendor_id) REFERENCES vendor(id)
);

CREATE INDEX idx_lot_code ON lot(lot_code);
CREATE INDEX idx_lot_item_id ON lot(item_id);
CREATE INDEX idx_lot_expiry ON lot(expiry_date);
```

#### Orders Table
```sql
CREATE TABLE order (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    total_amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quickbooks_synced BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (customer_id) REFERENCES customer(id)
);

CREATE INDEX idx_order_number ON order(order_number);
CREATE INDEX idx_order_customer ON order(customer_id);
CREATE INDEX idx_order_status ON order(status);
```

#### Customers Table
```sql
CREATE TABLE customer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    quickbooks_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customer_name ON customer(name);
CREATE INDEX idx_customer_email ON customer(email);
```

#### Printers Table
```sql
CREATE TABLE printer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    ip_address VARCHAR(15) NOT NULL,
    port INTEGER DEFAULT 9100,
    printer_type VARCHAR(20) DEFAULT 'zebra',
    label_width DECIMAL(4,2) DEFAULT 4.0,
    label_height DECIMAL(4,2) DEFAULT 2.0,
    dpi INTEGER DEFAULT 203,
    status VARCHAR(20) DEFAULT 'offline',
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_printer_ip ON printer(ip_address);
CREATE INDEX idx_printer_status ON printer(status);
```

### System Tables

#### Admin Users Table
```sql
CREATE TABLE admin_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

#### Sync Log Table
```sql
CREATE TABLE sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sync_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT,
    records_processed INTEGER DEFAULT 0,
    records_successful INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0
);

CREATE INDEX idx_sync_type ON sync_log(sync_type);
CREATE INDEX idx_sync_status ON sync_log(status);
CREATE INDEX idx_sync_timestamp ON sync_log(timestamp);
```

#### Schema Version Table
```sql
CREATE TABLE schema_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version INTEGER NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
```

---

## 🚀 Deployment

### Production Deployment
```bash
# Automated deployment
curl -sSL https://raw.githubusercontent.com/covxx/Paleta/refs/heads/master/scripts/deploy_production.sh | sudo bash
```

### Manual Deployment
```bash
# 1. Server preparation
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git nginx sqlite3

# 2. Application deployment
sudo useradd -m -s /bin/bash labelprinter
sudo mkdir -p /opt/label-printer
sudo chown labelprinter:labelprinter /opt/label-printer

# 3. Clone and setup
sudo -u labelprinter git clone https://github.com/covxx/Paleta.git /opt/label-printer
cd /opt/label-printer
sudo -u labelprinter python3 -m venv venv
sudo -u labelprinter ./venv/bin/pip install -r requirements.txt

# 4. Database initialization
sudo -u labelprinter python3 init_database_simple.py

# 5. Service configuration
sudo cp configs/label-printer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable label-printer

# 6. Nginx configuration
sudo cp configs/nginx.conf /etc/nginx/sites-available/label-printer
sudo ln -s /etc/nginx/sites-available/label-printer /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 7. SSL setup (optional)
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d app.srjlabs.dev

# 8. Start services
sudo systemctl start label-printer
sudo systemctl start nginx
```

### Update Process
```bash
# Safe production update
sudo ./scripts/update_production.sh
```

### Backup and Recovery
```bash
# Database backup
sudo -u labelprinter ./scripts/backup_database.sh

# Full system backup
sudo ./scripts/backup_system.sh

# Recovery
sudo ./scripts/rollback_production.sh
```

---

## 📊 Monitoring

### Health Checks
```bash
# Application health
curl http://localhost:5002/health

# System health check
./scripts/health_check.sh
```

### Logging
```bash
# Application logs
tail -f /opt/label-printer/logs/app.log

# System logs
journalctl -u label-printer -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Performance Monitoring
```bash
# System resources
htop
df -h
free -h

# Application performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5002/
```

### Metrics
- **Response Time**: < 500ms for API calls
- **Page Load Time**: < 2 seconds
- **Database Queries**: < 100ms
- **Memory Usage**: < 512MB typical
- **CPU Usage**: < 20% typical

---

## 🔒 Security

### Authentication
```python
# Session-based authentication
@app.route('/admin/login', methods=['POST'])
def admin_login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = AdminUser.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        session['admin_logged_in'] = True
        session['admin_email'] = user.email
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid credentials')
        return redirect(url_for('admin_login'))
```

### Authorization
```python
# Admin-only decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function
```

### Data Protection
- **Password Hashing**: bcrypt with salt
- **Session Security**: Secure session cookies
- **CSRF Protection**: CSRF tokens for forms
- **Input Validation**: Server-side validation
- **SQL Injection Prevention**: SQLAlchemy ORM

### Network Security
- **HTTPS**: SSL/TLS encryption
- **Firewall**: UFW configuration
- **Rate Limiting**: API rate limiting
- **Security Headers**: HTTP security headers

---

## 💻 Development

### Development Setup
```bash
# Clone repository
git clone https://github.com/covxx/Paleta.git
cd Paleta

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 init_database_simple.py

# Run development server
export FLASK_ENV=development
export FLASK_DEBUG=True
python3 app.py
```

### Code Structure
```
app/
├── app.py                 # Main application file
├── config.py             # Configuration settings
├── version.py            # Version management
├── changelog.py          # Changelog management
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Dashboard
│   ├── admin_*.html      # Admin pages
│   └── ...
├── static/               # Static files
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript
│   └── images/           # Images
├── instance/             # Instance files
│   └── inventory.db      # SQLite database
├── configs/              # Configuration files
│   ├── nginx.conf        # Nginx configuration
│   ├── gunicorn.conf.py  # Gunicorn configuration
│   └── label-printer.service # Systemd service
└── scripts/              # Utility scripts
    ├── deploy_production.sh
    ├── update_production.sh
    ├── backup_database.sh
    └── ...
```

### API Development
```python
# Adding new API endpoint
@app.route('/api/new-endpoint', methods=['GET', 'POST'])
@admin_required
def new_endpoint():
    if request.method == 'GET':
        # Handle GET request
        return jsonify({'success': True, 'data': []})
    elif request.method == 'POST':
        # Handle POST request
        data = request.json
        # Process data
        return jsonify({'success': True, 'message': 'Created'})
```

### Database Migrations
```python
# Adding new migration
def run_migration(version, description, migration_sql):
    print(f"\n=== Migration {version}: {description} ===")
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(migration_sql)
        conn.commit()
        print(f"✓ Migration {version} completed successfully")
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration {version} failed: {e}")
        raise
    finally:
        conn.close()
```

---

## 🔧 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check service status
sudo systemctl status label-printer

# Check logs
journalctl -u label-printer --no-pager

# Check dependencies
pip3 list | grep flask

# Check configuration
python3 -c "import app; print('Config OK')"
```

#### Database Issues
```bash
# Check database file
ls -la /opt/label-printer/instance/inventory.db

# Test database connection
sqlite3 /opt/label-printer/instance/inventory.db "SELECT 1;"

# Check database integrity
sqlite3 /opt/label-printer/instance/inventory.db "PRAGMA integrity_check;"

# Restore from backup
sudo ./scripts/rollback_production.sh
```

#### Nginx Issues
```bash
# Check Nginx configuration
sudo nginx -t

# Check Nginx status
sudo systemctl status nginx

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Reload Nginx
sudo systemctl reload nginx
```

#### QuickBooks Integration Issues
```bash
# Check QB connection
curl http://localhost:5002/api/quickbooks/status

# Check QB credentials
python3 -c "from app import QB_CLIENT_ID; print(QB_CLIENT_ID)"

# Test QB API
curl -X POST http://localhost:5002/api/quickbooks/test-connection
```

### Performance Issues
```bash
# Check system resources
htop
df -h
free -h

# Check application performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5002/

# Check database performance
sqlite3 /opt/label-printer/instance/inventory.db "EXPLAIN QUERY PLAN SELECT * FROM item;"

# Monitor logs
tail -f /opt/label-printer/logs/app.log
```

### Debug Mode
```bash
# Enable debug mode
export FLASK_ENV=development
export FLASK_DEBUG=True

# Run with debug
python3 app.py
```

### Log Analysis
```bash
# Application logs
grep "ERROR" /opt/label-printer/logs/app.log
grep "WARNING" /opt/label-printer/logs/app.log

# System logs
journalctl -u label-printer --since "1 hour ago" | grep ERROR

# Nginx logs
sudo grep "50[0-9]" /var/log/nginx/access.log
```

---

## 📈 Performance Optimization

### Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_item_name ON item(name);
CREATE INDEX idx_lot_expiry ON lot(expiry_date);
CREATE INDEX idx_order_status ON order(status);

-- Analyze query performance
EXPLAIN QUERY PLAN SELECT * FROM item WHERE name LIKE '%apple%';
```

### Application Optimization
```python
# Use connection pooling
from sqlalchemy.pool import QueuePool

# Optimize queries
items = Item.query.options(joinedload(Item.lots)).all()

# Use caching
from flask_caching import Cache
cache = Cache(app)

@cache.memoize(timeout=300)
def get_item_stats():
    return Item.query.count()
```

### Nginx Optimization
```nginx
# Enable gzip compression
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# Enable caching
location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

*This technical documentation provides comprehensive information for developers and administrators working with the ProduceFlow Label Printer system.*
