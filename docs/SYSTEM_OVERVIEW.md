# ProduceFlow Label Printer System - Complete Overview

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Core Features](#core-features)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [User Interface](#user-interface)
7. [QuickBooks Integration](#quickbooks-integration)
8. [Label Printing System](#label-printing-system)
9. [Admin Panel](#admin-panel)
10. [Deployment & Operations](#deployment--operations)
11. [Security](#security)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 System Overview

**ProduceFlow** is a comprehensive inventory management and label printing system designed for produce businesses. It provides real-time inventory tracking, order management, customer management, and automated label printing with QuickBooks integration.

### Key Capabilities
- **Inventory Management**: Track items, lots, vendors, and stock levels
- **Order Processing**: Create, manage, and fulfill customer orders
- **Label Printing**: Generate and print labels for inventory items
- **QuickBooks Sync**: Two-way synchronization with QuickBooks Online
- **Admin Dashboard**: Comprehensive management interface
- **Multi-user Support**: Role-based access control

---

## 🏗️ Architecture

### Technology Stack
- **Backend**: Python Flask
- **Database**: SQLite (production-ready with backup system)
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap 5)
- **Printing**: ZPL (Zebra Programming Language)
- **Integration**: QuickBooks Online API
- **Deployment**: Ubuntu VPS with Nginx, Gunicorn

### System Components
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
```

---

## 🔌 API Endpoints

### Core API Endpoints

#### Items API
- `GET /api/items` - Get all items
- `POST /api/items` - Create new item
- `PUT /api/items/<id>` - Update item
- `DELETE /api/items/<id>` - Delete item

#### LOTs API
- `GET /api/lots` - Get all lots
- `POST /api/lots` - Create new lot
- `PUT /api/lots/<id>` - Update lot
- `DELETE /api/lots/<id>` - Delete lot

#### Orders API
- `GET /api/orders` - Get all orders
- `POST /api/orders` - Create new order
- `PUT /api/orders/<id>` - Update order
- `DELETE /api/orders/<id>` - Delete order

#### Printers API
- `GET /api/printers` - Get all printers
- `POST /api/printers` - Create new printer
- `PUT /api/printers/<id>` - Update printer
- `DELETE /api/printers/<id>` - Delete printer
- `POST /api/printers/<id>/test` - Test printer connection

### QuickBooks API Endpoints
- `GET /api/quickbooks/status` - Get sync status
- `POST /api/quickbooks/connect` - Connect to QuickBooks
- `POST /api/quickbooks/disconnect` - Disconnect from QuickBooks
- `POST /api/quickbooks/sync/items` - Sync items
- `POST /api/quickbooks/sync/customers` - Sync customers
- `POST /api/quickbooks/sync/orders` - Sync orders
- `GET /api/quickbooks/synced-items` - Get synced items
- `GET /api/quickbooks/sync/log` - Get sync log

---

## 🖥️ User Interface

### Main Application Pages

#### Dashboard (`/`)
- **Overview**: System statistics and quick actions
- **Recent Activity**: Latest system events
- **System Status**: Health checks and status indicators
- **Quick Actions**: Direct links to common tasks

#### Receiving (`/receiving`)
- **LOT Creation**: Add new inventory lots
- **Vendor Management**: Manage suppliers
- **Item Management**: Add/edit products
- **Batch Operations**: Bulk lot creation

#### Orders (`/orders`)
- **Order List**: View all orders with filtering
- **Order Details**: Detailed order information
- **Status Updates**: Change order status
- **Print Labels**: Generate order labels

#### Order Entry (`/orders/new`)
- **Customer Selection**: Choose or create customers
- **Item Selection**: Add items to order
- **Quantity Management**: Set quantities and prices
- **Order Summary**: Review and confirm order

#### Customers (`/customers`)
- **Customer List**: View all customers
- **Customer Details**: Contact and order history
- **QuickBooks Sync**: Sync customer data
- **Search & Filter**: Find customers quickly

### Admin Panel Pages

#### Admin Dashboard (`/admin`)
- **System Overview**: Key metrics and statistics
- **Quick Actions**: Direct access to management functions
- **Health Status**: System health indicators
- **Recent Activity**: Admin activity log

#### Items Management (`/admin/items`)
- **Item Catalog**: Complete product database
- **Bulk Operations**: Mass updates and imports
- **Category Management**: Organize products
- **QuickBooks Sync**: Sync item data

#### LOT Management (`/admin/lots`)
- **LOT Tracking**: Monitor all inventory lots
- **Expiry Management**: Track expiration dates
- **Vendor Tracking**: Monitor supplier performance
- **Status Updates**: Change lot status

#### Printer Management (`/admin/printers`)
- **Printer Configuration**: Setup and manage printers
- **Connection Testing**: Test printer connectivity
- **Label Templates**: Customize label designs
- **Print Queue**: Monitor print jobs

#### QuickBooks Admin (`/quickbooks-admin`)
- **Connection Status**: Monitor QB connection
- **Sync Management**: Control data synchronization
- **Sync Logs**: View sync history and errors
- **Data Mapping**: Configure field mappings

---

## 🔗 QuickBooks Integration

### Connection Process
1. **OAuth Authentication**: Secure connection to QuickBooks Online
2. **Company Selection**: Choose QuickBooks company
3. **Permission Granting**: Authorize data access
4. **Token Storage**: Secure storage of access tokens

### Data Synchronization

#### Customer Sync
- **Bidirectional**: Sync customers both ways
- **Field Mapping**: Map custom fields
- **Conflict Resolution**: Handle data conflicts
- **Sync Logging**: Track all sync operations

#### Item Sync
- **Product Catalog**: Sync inventory items
- **Pricing Updates**: Keep prices synchronized
- **Category Mapping**: Map product categories
- **GTIN Management**: Handle barcode data

#### Order Sync
- **Order Export**: Send orders to QuickBooks
- **Invoice Creation**: Generate QB invoices
- **Payment Tracking**: Monitor payment status
- **Status Updates**: Sync order status changes

### Sync Management
- **Manual Sync**: Trigger sync operations manually
- **Automatic Sync**: Scheduled background sync
- **Error Handling**: Retry failed syncs
- **Data Validation**: Ensure data integrity

---

## 🖨️ Label Printing System

### ZPL Generation
```python
def generate_zpl(item, lot, printer):
    zpl = f"""
    ^XA
    ^FO50,50^A0N,30,30^FD{item.name}^FS
    ^FO50,100^A0N,20,20^FD{lot.lot_code}^FS
    ^FO50,150^A0N,20,20^FD{lot.expiry_date}^FS
    ^FO50,200^BY3^BCN,50,Y,N,N^FD{lot.lot_code}^FS
    ^XZ
    """
    return zpl
```

### Printer Management
- **Network Printers**: IP-based printer connections
- **Connection Testing**: Verify printer connectivity
- **Status Monitoring**: Track printer status
- **Error Handling**: Handle print failures

### Label Templates
- **Customizable**: Modify label layouts
- **Multiple Formats**: Support different label sizes
- **Barcode Integration**: Include barcodes and QR codes
- **Branding**: Add company logos and information

---

## 👨‍💼 Admin Panel

### Access Control
- **Admin Authentication**: Secure login system
- **Session Management**: Secure session handling
- **Role-based Access**: Different permission levels
- **Activity Logging**: Track admin actions

### Management Functions

#### System Management
- **User Management**: Manage system users
- **Printer Configuration**: Setup and configure printers
- **System Settings**: Configure application settings
- **Backup Management**: Manage system backups

#### Data Management
- **Bulk Operations**: Mass data operations
- **Data Import/Export**: CSV import/export
- **Data Validation**: Ensure data integrity
- **Cleanup Tools**: Remove old data

#### Monitoring
- **System Health**: Monitor system performance
- **Error Logs**: View and analyze errors
- **Usage Statistics**: Track system usage
- **Performance Metrics**: Monitor response times

---

## 🚀 Deployment & Operations

### Production Deployment
```bash
# One-command deployment
curl -sSL https://raw.githubusercontent.com/covxx/Paleta/refs/heads/master/scripts/deploy_production.sh | sudo bash
```

### Update System
```bash
# Safe production updates
sudo ./scripts/update_production.sh
```

### Backup System
```bash
# Database backup
sudo -u labelprinter ./scripts/backup_database.sh

# Full system backup
sudo ./scripts/backup_system.sh
```

### Health Monitoring
```bash
# System health check
./scripts/health_check.sh

# Service monitoring
sudo systemctl status label-printer
```

### Log Management
- **Application Logs**: `/opt/label-printer/logs/`
- **System Logs**: `journalctl -u label-printer`
- **Nginx Logs**: `/var/log/nginx/`
- **Error Tracking**: Centralized error logging

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

### Access Control
- **Admin-only Areas**: Restricted admin functions
- **API Authentication**: Secure API access
- **File Permissions**: Proper file permissions
- **User Isolation**: Isolated user accounts

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
```

#### Database Issues
```bash
# Check database file
ls -la /opt/label-printer/instance/inventory.db

# Test database connection
sqlite3 /opt/label-printer/instance/inventory.db "SELECT 1;"

# Restore from backup
sudo ./scripts/rollback_production.sh
```

#### Printer Issues
```bash
# Test printer connection
telnet <printer_ip> 9100

# Check printer status
curl -X POST http://localhost:5002/api/printers/1/test

# View printer logs
tail -f /opt/label-printer/logs/printer.log
```

#### QuickBooks Sync Issues
```bash
# Check QB connection
curl http://localhost:5002/api/quickbooks/status

# View sync logs
curl http://localhost:5002/api/quickbooks/sync/log

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

# Monitor logs
tail -f /opt/label-printer/logs/app.log
```

### Recovery Procedures
```bash
# Full system recovery
sudo ./scripts/rollback_production.sh

# Database recovery
sudo -u labelprinter cp /opt/label-printer/backups/latest_backup.db /opt/label-printer/instance/inventory.db

# Service restart
sudo systemctl restart label-printer
sudo systemctl restart nginx
```

---

## 📊 System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04 LTS or later
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 20GB minimum, 50GB recommended
- **Network**: Stable internet connection
- **CPU**: 2 cores minimum, 4 cores recommended

### Recommended Setup
- **OS**: Ubuntu 22.04 LTS
- **RAM**: 8GB
- **Storage**: 100GB SSD
- **Network**: 100Mbps connection
- **CPU**: 4 cores, 2.4GHz

### Dependencies
- **Python**: 3.8 or later
- **Nginx**: 1.18 or later
- **Gunicorn**: 20.1 or later
- **SQLite**: 3.31 or later

---

## 📈 Performance Metrics

### Typical Performance
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

## 🔄 Maintenance

### Daily Tasks
- **Health Check**: Run health check script
- **Log Review**: Check for errors
- **Backup Verification**: Confirm backups are working
- **Performance Monitoring**: Check response times

### Weekly Tasks
- **System Updates**: Update system packages
- **Log Cleanup**: Clean old log files
- **Database Optimization**: Optimize database
- **Security Updates**: Apply security patches

### Monthly Tasks
- **Full Backup**: Create full system backup
- **Performance Review**: Analyze performance metrics
- **Security Audit**: Review security settings
- **Capacity Planning**: Monitor disk space and usage

---

## 📞 Support

### Documentation
- **User Manual**: Complete user guide
- **API Documentation**: API reference
- **Deployment Guide**: Installation instructions
- **Troubleshooting Guide**: Common issues and solutions

### Monitoring
- **Health Checks**: Automated health monitoring
- **Error Tracking**: Centralized error logging
- **Performance Metrics**: System performance tracking
- **Usage Analytics**: User activity monitoring

### Backup & Recovery
- **Automated Backups**: Daily database backups
- **Point-in-time Recovery**: Restore to any backup
- **Disaster Recovery**: Complete system recovery
- **Data Migration**: Easy data migration tools

---

*This document provides a comprehensive overview of the ProduceFlow Label Printer System. For specific implementation details, refer to the individual component documentation and API references.*
