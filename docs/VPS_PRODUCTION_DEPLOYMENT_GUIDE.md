# VPS Production Deployment Guide - app.srjlabs.dev

Complete guide for deploying the QuickBooks Label Printer system on a VPS with production configuration for the domain `app.srjlabs.dev`.

## 🚀 **Quick Start**

### **Prerequisites**
- Ubuntu 20.04+ VPS with 4+ cores
- Root or sudo access
- Domain `app.srjlabs.dev` pointing to your VPS IP
- Let's Encrypt SSL certificate capability

### **One-Command Deployment**
```bash
# Download and run the production setup script
curl -fsSL https://raw.githubusercontent.com/covxx/Paleta/refs/heads/master/scripts/deploy_production.sh | bash
```

### **Manual Setup**
```bash
# Clone the repository
git clone https://github.com/covxx/Paleta.git
cd Paleta

# Run production deployment script
sudo ./scripts/deploy_production.sh -d app.srjlabs.dev -e admin@srjlabs.dev
```

## 📋 **Production Architecture**

### **System Components**
- **Nginx**: Reverse proxy with SSL termination
- **Gunicorn**: WSGI server with 4 workers (optimized for 4-core VPS)
- **SQLite**: Database with connection pooling
- **Systemd**: Service management
- **Let's Encrypt**: SSL certificate management
- **UFW**: Firewall configuration

### **Port Configuration**
- **Port 80**: Nginx (HTTP - redirects to HTTPS)
- **Port 443**: Nginx (HTTPS)
- **Port 5002**: Gunicorn (internal)
- **Port 22**: SSH (firewall protected)

## ⚙️ **Configuration Files**

### **Production Configuration**
- `configs/config_production.py`: Production settings optimized for VPS
- `configs/gunicorn.conf.py`: Gunicorn configuration with 4 workers
- `configs/nginx.conf`: Nginx reverse proxy with SSL
- `configs/label-printer.service`: Systemd service file

### **Key Optimizations**
- **4 Gunicorn workers** (matching VPS core count)
- **Connection pooling** for database efficiency
- **SSL/TLS termination** at Nginx level
- **Rate limiting** to prevent abuse
- **Gzip compression** for faster responses
- **Security headers** for protection
- **Automatic SSL renewal** with Let's Encrypt

## 🔧 **Deployment Steps**

### **1. System Preparation**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    build-essential nginx git curl wget unzip sqlite3 libsqlite3-dev \
    pkg-config libcairo2-dev libjpeg-dev libgif-dev libpango1.0-dev \
    libgdk-pixbuf2.0-dev libffi-dev shared-mime-info certbot \
    python3-certbot-nginx ufw
```

### **2. Application Setup**
```bash
# Create application user
sudo useradd -r -s /bin/bash -d /opt/label-printer -m labelprinter

# Create application directory
sudo mkdir -p /opt/label-printer
sudo chown labelprinter:labelprinter /opt/label-printer

# Clone repository
sudo -u labelprinter git clone https://github.com/yourusername/label-printer.git /opt/label-printer

# Setup Python environment
cd /opt/label-printer
sudo -u labelprinter python3 -m venv venv
sudo -u labelprinter bash -c "source venv/bin/activate && pip install --upgrade pip"
sudo -u labelprinter bash -c "source venv/bin/activate && pip install -r requirements.txt"
```

### **3. Database Initialization**
```bash
# Initialize database
sudo -u labelprinter bash -c "cd /opt/label-printer && source venv/bin/activate && python init_database_simple.py"
```

### **4. Systemd Service Configuration**
```bash
# Create systemd service file
sudo tee /etc/systemd/system/label-printer.service > /dev/null <<EOF
[Unit]
Description=QuickBooks Label Printer
After=network.target

[Service]
Type=simple
User=labelprinter
Group=labelprinter
WorkingDirectory=/opt/label-printer
Environment=PATH=/opt/label-printer/venv/bin
Environment=FLASK_ENV=production
Environment=FLASK_APP=app.py
ExecStart=/opt/label-printer/venv/bin/gunicorn --config configs/gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/label-printer

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable label-printer
sudo systemctl start label-printer
```

### **5. Nginx Configuration**
```bash
# Create Nginx configuration for app.srjlabs.dev
sudo tee /etc/nginx/sites-available/label-printer > /dev/null <<EOF
# Rate limiting zones
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=uploads:10m rate=2r/s;

# HTTP server - redirect to HTTPS
server {
    listen 80;
    server_name app.srjlabs.dev www.app.srjlabs.dev;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name app.srjlabs.dev www.app.srjlabs.dev;
    
    # SSL configuration (will be updated by certbot)
    ssl_certificate /etc/letsencrypt/live/app.srjlabs.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.srjlabs.dev/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Client settings
    client_max_body_size 16M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Static files
    location /static/ {
        alias /opt/label-printer/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Upload files
    location /uploads/ {
        alias /opt/label-printer/uploads/;
        expires 1d;
        add_header Cache-Control "public";
    }
    
    # API endpoints with rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Upload endpoints with stricter rate limiting
    location /upload {
        limit_req zone=uploads burst=5 nodelay;
        
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Longer timeouts for file uploads
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        # Disable buffering for uploads
        proxy_request_buffering off;
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host \$host;
    }
    
    # Deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ \.(py|pyc|pyo|pyd|log|sql|db)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/label-printer /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t
```

### **6. SSL Certificate Setup**
```bash
# Obtain SSL certificate from Let's Encrypt
sudo certbot --nginx -d app.srjlabs.dev -d www.app.srjlabs.dev --non-interactive --agree-tos --email admin@srjlabs.dev

# Test automatic renewal
sudo certbot renew --dry-run

# Setup automatic renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **7. Firewall Configuration**
```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

### **8. Start Services**
```bash
# Start and enable services
sudo systemctl start label-printer
sudo systemctl start nginx
sudo systemctl enable label-printer
sudo systemctl enable nginx

# Check service status
sudo systemctl status label-printer
sudo systemctl status nginx
```

## 🔒 **Security Configuration**

### **Environment Variables**
Create `/opt/label-printer/.env`:
```bash
# QuickBooks API
QB_CLIENT_ID=your_client_id
QB_CLIENT_SECRET=your_client_secret
QB_COMPANY_ID=your_company_id
QB_SANDBOX=false

# Security
SECRET_KEY=your-super-secret-production-key-change-this
ADMIN_EMAIL=admin@srjlabs.dev
ADMIN_PASSWORD=your_secure_admin_password

# Database
DATABASE_URI=sqlite:///instance/inventory.db

# Email (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

### **File Permissions**
```bash
# Set proper file permissions
sudo chown -R labelprinter:labelprinter /opt/label-printer
sudo chmod -R 755 /opt/label-printer
sudo chmod 600 /opt/label-printer/.env
```

## 📊 **Monitoring & Logging**

### **Service Status**
```bash
# Check application status
sudo systemctl status label-printer

# Check Nginx status
sudo systemctl status nginx

# View application logs
sudo journalctl -u label-printer -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### **Performance Monitoring**
```bash
# System resources
htop

# Network usage
nethogs

# Disk I/O
iotop

# Application health
curl -s https://app.srjlabs.dev/health | python3 -m json.tool
```

## 🔄 **Backup & Recovery**

### **Automatic Backups**
```bash
# Create backup script
sudo tee /opt/label-printer/backup.sh > /dev/null <<EOF
#!/bin/bash
# Backup script for QuickBooks Label Printer

BACKUP_DIR="/opt/backups/label-printer"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_\$DATE.tar.gz"

# Create backup directory
mkdir -p \$BACKUP_DIR

# Create backup
tar -czf \$BACKUP_DIR/\$BACKUP_FILE \\
    -C /opt/label-printer \\
    --exclude=venv \\
    --exclude=__pycache__ \\
    --exclude=*.pyc \\
    .

# Keep only last 30 days of backups
find \$BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete

echo "Backup created: \$BACKUP_FILE"
EOF

sudo chmod +x /opt/label-printer/backup.sh
sudo chown labelprinter:labelprinter /opt/label-printer/backup.sh

# Schedule daily backups
sudo -u labelprinter crontab -e
# Add: 0 2 * * * /opt/label-printer/backup.sh
```

## 🚀 **Performance Optimization**

### **Gunicorn Configuration**
- **4 worker processes** (matches VPS cores)
- **2 threads per worker** (8 concurrent requests)
- **1000 worker connections**
- **30-second timeout**
- **Memory limit**: 200MB per worker

### **Nginx Optimization**
- **Gzip compression** enabled
- **Static file caching** (1 year)
- **Client max body size**: 16MB
- **Connection keep-alive**
- **Buffer optimization**

### **Database Optimization**
- **Connection pooling** enabled
- **Query optimization**
- **Regular maintenance** scheduled

## 🔧 **Maintenance**

### **Regular Updates**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update application
cd /opt/label-printer
sudo -u labelprinter git pull origin main
sudo -u labelprinter bash -c "source venv/bin/activate && pip install -r requirements.txt"

# Restart services
sudo systemctl restart label-printer
sudo systemctl reload nginx
```

### **SSL Certificate Renewal**
```bash
# Manual renewal
sudo certbot renew

# Check renewal status
sudo certbot certificates
```

### **Database Maintenance**
```bash
# SQLite maintenance
sudo -u labelprinter sqlite3 /opt/label-printer/instance/inventory.db "VACUUM;"
sudo -u labelprinter sqlite3 /opt/label-printer/instance/inventory.db "ANALYZE;"
```

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Service Won't Start**
```bash
# Check service status
sudo systemctl status label-printer

# Check logs
sudo journalctl -u label-printer -n 50

# Check configuration
sudo -u labelprinter /opt/label-printer/venv/bin/python -c "import app"
```

#### **Nginx Errors**
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Reload configuration
sudo systemctl reload nginx
```

#### **SSL Issues**
```bash
# Check certificate status
sudo certbot certificates

# Test SSL configuration
openssl s_client -connect app.srjlabs.dev:443 -servername app.srjlabs.dev

# Renew certificate
sudo certbot renew --force-renewal
```

#### **Database Issues**
```bash
# Check database file
ls -la /opt/label-printer/instance/inventory.db

# Check permissions
sudo -u labelprinter sqlite3 /opt/label-printer/instance/inventory.db ".tables"
```

## 📈 **Scaling**

### **Vertical Scaling**
- Increase VPS resources (CPU, RAM, storage)
- Optimize database queries
- Add caching layer (Redis)
- Use CDN for static files

### **Horizontal Scaling**
- Load balancer (HAProxy/Nginx)
- Multiple application instances
- Database clustering
- Session storage (Redis)

## 🔐 **Security Best Practices**

### **System Security**
- Regular security updates
- Firewall configuration (UFW)
- SSH key authentication
- Fail2ban installation
- Regular security audits

### **Application Security**
- Input validation
- SQL injection prevention
- XSS protection
- CSRF protection
- Rate limiting
- Secure headers

### **Data Security**
- Encrypted backups
- Secure file permissions
- Regular security scans
- Access logging
- Incident response plan

## 📞 **Support**

### **Useful Commands**
```bash
# Restart application
sudo systemctl restart label-printer

# Check service status
sudo systemctl status label-printer

# View real-time logs
sudo journalctl -u label-printer -f

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Check SSL certificate
sudo certbot certificates

# Check system resources
htop
free -h
df -h
```

### **Log Locations**
- **Application logs**: `sudo journalctl -u label-printer`
- **Nginx logs**: `/var/log/nginx/`
- **SSL logs**: `/var/log/letsencrypt/`
- **System logs**: `/var/log/`

### **Configuration Files**
- **Application**: `/opt/label-printer/`
- **Nginx**: `/etc/nginx/sites-available/label-printer`
- **Systemd**: `/etc/systemd/system/label-printer.service`
- **SSL**: `/etc/letsencrypt/live/app.srjlabs.dev/`
- **Environment**: `/opt/label-printer/.env`

## 🎯 **Access Information**

### **After Deployment**
- **Web Interface**: `https://app.srjlabs.dev`
- **Admin Login**: `https://app.srjlabs.dev/admin/login`
- **API Endpoints**: `https://app.srjlabs.dev/api/*`
- **Health Check**: `https://app.srjlabs.dev/health`

### **Service Management**
```bash
# Start/Stop/Restart
sudo systemctl start label-printer
sudo systemctl stop label-printer
sudo systemctl restart label-printer

# Check Status
sudo systemctl status label-printer

# View Logs
sudo journalctl -u label-printer -f
```

---

**Your QuickBooks Label Printer system is now production-ready at https://app.srjlabs.dev!** 🚀

The system includes:
- ✅ SSL/HTTPS with Let's Encrypt
- ✅ Production-optimized configuration
- ✅ Security hardening
- ✅ Performance optimization
- ✅ Monitoring and logging
- ✅ Backup and recovery
- ✅ Firewall configuration
- ✅ Service management
- ✅ Comprehensive documentation
