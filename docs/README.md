# ProduceFlow Label Printer System

## 🎯 Overview

**ProduceFlow** is a comprehensive inventory management and label printing system designed specifically for produce businesses. It provides real-time inventory tracking, order management, customer management, and automated label printing with seamless QuickBooks integration.

### Key Features
- **📦 Inventory Management**: Track items, lots, vendors, and stock levels
- **🛒 Order Processing**: Create, manage, and fulfill customer orders
- **🖨️ Label Printing**: Generate and print labels for inventory items
- **🔗 QuickBooks Sync**: Two-way synchronization with QuickBooks Online
- **👨‍💼 Admin Dashboard**: Comprehensive management interface
- **👥 Multi-user Support**: Role-based access control
- **📱 Mobile Responsive**: Works on all devices
- **🔒 Enterprise Security**: Secure authentication and data protection

---

## 🚀 Quick Start

### One-Command Installation
```bash
curl -sSL https://raw.githubusercontent.com/covxx/Paleta/refs/heads/master/scripts/deploy_production.sh | sudo bash
```

### Access the System
- **Production URL**: `https://app.srjlabs.dev`
- **Admin Panel**: `https://app.srjlabs.dev/admin`
- **QuickBooks Admin**: `https://app.srjlabs.dev/quickbooks-admin`

### First Time Setup
1. **Configure Printers**: Admin Panel → Printer Management
2. **Add Items**: Receiving → Add Items
3. **Setup Vendors**: Receiving → Manage Vendors
4. **Connect QuickBooks**: Admin Panel → QuickBooks Admin

---

## 📚 Documentation

### User Documentation
- **[User Manual](USER_MANUAL.md)** - Complete user guide for daily operations
- **[Quick Reference](QUICK_REFERENCE.md)** - Essential commands and procedures
- **[System Overview](SYSTEM_OVERVIEW.md)** - Comprehensive system documentation

### Technical Documentation
- **[Technical Documentation](TECHNICAL_DOCUMENTATION.md)** - Developer and administrator guide
- **[Deployment Guide](VPS_PRODUCTION_DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[Quick Deployment Guide](QUICK_DEPLOYMENT_GUIDE.md)** - Fast deployment setup

### Specialized Guides
- **[QuickBooks Setup](QUICKBOOKS_SETUP.md)** - QuickBooks integration guide
- **[SSL Integration Guide](SSL_INTEGRATION_GUIDE.md)** - SSL certificate setup
- **[Update System Summary](UPDATE_SYSTEM_SUMMARY.md)** - System update procedures

---

## 🏗️ System Architecture

### Technology Stack
- **Backend**: Python Flask
- **Database**: SQLite (production-ready with backup system)
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap 5)
- **Printing**: ZPL (Zebra Programming Language)
- **Integration**: QuickBooks Online API
- **Deployment**: Ubuntu VPS with Nginx, Gunicorn

### Core Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Mobile App    │    │  Admin Panel    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      Nginx Proxy          │
                    │   (SSL Termination)       │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    Flask Application      │
                    │   (Gunicorn WSGI)         │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     SQLite Database       │
                    │   (Inventory & Orders)    │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   QuickBooks Online API   │
                    │   (Customer & Item Sync)  │
                    └───────────────────────────┘
```

---

## ⚙️ Core Features

### 1. Inventory Management
- **Items**: Product catalog with GTIN, categories, and pricing
- **LOTs**: Batch tracking with expiry dates and quantities
- **Vendors**: Supplier management with contact information
- **Stock Levels**: Real-time inventory tracking

### 2. Order Management
- **Order Creation**: Customer order entry with item selection
- **Order Fulfillment**: Pick, pack, and ship workflow
- **Order Tracking**: Status updates and history
- **Customer Management**: Customer database with contact info

### 3. Label Printing
- **ZPL Generation**: Automatic label creation
- **Printer Management**: Multiple printer support
- **Label Templates**: Customizable label designs
- **Batch Printing**: Print multiple labels at once

### 4. QuickBooks Integration
- **Customer Sync**: Two-way customer synchronization
- **Item Sync**: Product catalog synchronization
- **Order Sync**: Order data transfer to QuickBooks
- **Pricing Sync**: Price updates and management

---

## 🗄️ Database Schema

### Core Tables
- **Items**: Product catalog with pricing and categories
- **LOTs**: Inventory batches with expiry dates
- **Orders**: Customer orders with status tracking
- **Customers**: Customer database with contact info
- **Printers**: Printer configuration and status
- **Vendors**: Supplier management
- **Sync Logs**: QuickBooks synchronization history

### Data Relationships
```
Items (1) ←→ (Many) LOTs
Items (1) ←→ (Many) Order Items
Customers (1) ←→ (Many) Orders
Vendors (1) ←→ (Many) LOTs
Printers (1) ←→ (Many) Print Jobs
```

---

## 🔌 API Endpoints

### Core API
- **Items API**: `/api/items` (GET, POST, PUT, DELETE)
- **LOTs API**: `/api/lots` (GET, POST, PUT, DELETE)
- **Orders API**: `/api/orders` (GET, POST, PUT, DELETE)
- **Customers API**: `/api/customers` (GET, POST, PUT, DELETE)
- **Printers API**: `/api/printers` (GET, POST, PUT, DELETE)

### QuickBooks API
- **Connection**: `/api/quickbooks/connect`, `/api/quickbooks/disconnect`
- **Sync**: `/api/quickbooks/sync/items`, `/api/quickbooks/sync/customers`
- **Status**: `/api/quickbooks/status`, `/api/quickbooks/sync/log`

### System API
- **Health**: `/health`
- **Version**: `/api/version`
- **Statistics**: `/api/statistics`

---

## 🖥️ User Interface

### Main Application
- **Dashboard**: System overview and quick actions
- **Receiving**: Inventory management and LOT creation
- **Orders**: Order management and fulfillment
- **Customers**: Customer database management
- **Order Entry**: Create new customer orders

### Admin Panel
- **Admin Dashboard**: System management overview
- **Items Management**: Product catalog management
- **LOT Management**: Inventory batch tracking
- **Vendor Management**: Supplier management
- **Printer Management**: Printer configuration
- **User Management**: Active user monitoring
- **QuickBooks Admin**: QB integration management

---

## 🔗 QuickBooks Integration

### Connection Process
1. **OAuth Authentication**: Secure connection to QuickBooks Online
2. **Company Selection**: Choose QuickBooks company
3. **Permission Granting**: Authorize data access
4. **Token Storage**: Secure storage of access tokens

### Data Synchronization
- **Customer Sync**: Bidirectional customer synchronization
- **Item Sync**: Product catalog synchronization
- **Order Sync**: Order data transfer to QuickBooks
- **Pricing Sync**: Price updates and management

### Sync Management
- **Manual Sync**: Trigger sync operations manually
- **Automatic Sync**: Scheduled background sync
- **Error Handling**: Retry failed syncs
- **Data Validation**: Ensure data integrity

---

## 🖨️ Label Printing System

### ZPL Generation
- **Automatic Labels**: Generate labels from LOT data
- **Custom Templates**: Customizable label designs
- **Barcode Integration**: Include barcodes and QR codes
- **Branding**: Add company logos and information

### Printer Management
- **Network Printers**: IP-based printer connections
- **Connection Testing**: Verify printer connectivity
- **Status Monitoring**: Track printer status
- **Error Handling**: Handle print failures

### Supported Printers
- **Zebra**: ZD420, ZD620, ZT230, ZT410
- **Datamax**: I-Class, E-Class
- **Intermec**: PC43, PC43d
- **Other**: Generic ZPL-compatible printers

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

### Update System
```bash
# Safe production updates
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

## 🔒 Security

### Authentication
- **Admin Login**: Secure admin authentication
- **Session Management**: Secure session handling
- **Password Security**: Strong password requirements
- **Session Timeout**: Automatic session expiration

### Data Protection
- **Database Encryption**: SQLite with encryption
- **Backup Encryption**: Encrypted backup files
- **SSL/TLS**: HTTPS encryption for all traffic
- **API Security**: Secure API endpoints

### Network Security
- **Firewall**: UFW firewall configuration
- **Port Management**: Only necessary ports open
- **SSL Certificates**: Let's Encrypt SSL
- **Security Headers**: HTTP security headers

---

## 📊 Performance

### System Requirements
- **OS**: Ubuntu 20.04 LTS or later
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 20GB minimum, 50GB recommended
- **Network**: Stable internet connection
- **CPU**: 2 cores minimum, 4 cores recommended

### Performance Metrics
- **Page Load Time**: < 2 seconds
- **API Response Time**: < 500ms
- **Database Queries**: < 100ms
- **Label Generation**: < 1 second
- **QuickBooks Sync**: 2-5 seconds per item

### Scalability
- **Concurrent Users**: 50+ users
- **Database Size**: 100MB+ supported
- **Order Volume**: 1000+ orders per day
- **Item Catalog**: 10,000+ items
- **LOT Tracking**: 100,000+ lots

---

## 🔧 Troubleshooting

### Common Issues
- **Application Won't Start**: Check service status and logs
- **Database Issues**: Verify database file and integrity
- **Printer Issues**: Test printer connection and configuration
- **QuickBooks Sync Issues**: Check connection status and credentials

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

---

## 📈 Monitoring

### Health Monitoring
- **Service Status**: Systemd service monitoring
- **Database Health**: Connection and integrity checks
- **Printer Status**: Network connectivity monitoring
- **QuickBooks Sync**: Sync status and error tracking

### Performance Monitoring
- **Response Times**: API and page load times
- **Resource Usage**: CPU, memory, and disk usage
- **Error Rates**: Application and system errors
- **User Activity**: Active users and session tracking

### Alerting
- **Service Down**: Automatic service restart
- **Database Issues**: Backup and recovery procedures
- **Sync Errors**: QuickBooks sync failure alerts
- **Performance Issues**: Resource usage alerts

---

## 🆘 Support

### Documentation
- **User Manual**: Complete user guide
- **Technical Documentation**: Developer and administrator guide
- **Quick Reference**: Essential commands and procedures
- **API Documentation**: API reference and examples

### Support Channels
- **Email Support**: support@srjlabs.dev
- **Phone Support**: (555) 123-4567
- **Emergency Support**: 24/7 emergency support
- **Documentation**: Comprehensive online documentation

### Community
- **GitHub Repository**: https://github.com/covxx/Paleta
- **Issue Tracking**: GitHub Issues
- **Feature Requests**: GitHub Discussions
- **Contributions**: Pull requests welcome

---

## 📋 Roadmap

### Current Version: v0.5.0
- ✅ Core inventory management
- ✅ Order processing
- ✅ Label printing
- ✅ QuickBooks integration
- ✅ Admin panel
- ✅ Mobile responsive design

### Upcoming Features
- 🔄 Advanced reporting and analytics
- 🔄 Barcode scanning integration
- 🔄 Mobile app (iOS/Android)
- 🔄 Multi-location support
- 🔄 Advanced user roles and permissions
- 🔄 API rate limiting and throttling
- 🔄 Real-time notifications
- 🔄 Advanced label templates

### Long-term Goals
- 🔄 Machine learning for demand forecasting
- 🔄 IoT integration for temperature monitoring
- 🔄 Advanced supply chain management
- 🔄 Integration with other ERP systems
- 🔄 Cloud-based deployment options
- 🔄 Advanced security features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

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

---

## 📞 Contact

- **Project Maintainer**: [Your Name]
- **Email**: admin@srjlabs.dev
- **Website**: https://app.srjlabs.dev
- **GitHub**: https://github.com/covxx/Paleta

---

*ProduceFlow Label Printer System - Streamlining produce business operations with modern technology.*