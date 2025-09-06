# Database Initialization Fix Guide - QuickBooks Label Printer

## 🚨 **Issue Identified**

The database setup failed with this error:
```
[INFO] Setting up database...
Traceback (most recent call last):
  File "<string>", line 2, in <module>
  File "/opt/label-printer/app.py", line 27, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'
```

This happens because the database initialization is trying to import the full Flask app before all Python dependencies are properly installed in the virtual environment.

## 🔧 **Quick Fix Solution**

### **Option 1: Use the Database Fix Script (Recommended)**

I've created a dedicated fix script. Run this on your VPS:

```bash
# Run the database fix script
sudo ./fix_database_init.sh fix
```

### **Option 2: Manual Fix Commands**

If you prefer to fix manually, run these commands on your VPS:

```bash
# Install missing dependencies
sudo -u labelprinter -H bash -c "cd /opt/label-printer && source venv/bin/activate && pip install -r requirements.txt"

# Initialize database
sudo -u labelprinter -H bash -c "cd /opt/label-printer && source venv/bin/activate && python init_database.py"
```

### **Option 3: Re-run the Updated VPS Setup Script**

The VPS setup script has been updated to handle database initialization correctly. You can re-run it:

```bash
# Re-run the updated setup script
sudo ./vps_setup.sh
```

## 📋 **What Was Fixed**

### **1. Created Dedicated Database Initialization Script (`init_database.py`)**

**Features**:
- ✅ **Standalone**: Doesn't import the full Flask app
- ✅ **Self-contained**: Includes all necessary model definitions
- ✅ **Error handling**: Graceful error handling and reporting
- ✅ **Initial data**: Creates default printer and sync status records
- ✅ **Verification**: Tests database creation and connection

### **2. Updated VPS Setup Script (`vps_setup.sh`)**

**Before (Problematic)**:
```bash
sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && source venv/bin/activate && python -c '
from app import app, db  # This failed because requests wasn't installed
with app.app_context():
    db.create_all()
'
"
```

**After (Fixed)**:
```bash
# Use dedicated database initialization script
sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && source venv/bin/activate && python init_database.py"
```

### **3. Created Database Fix Script (`fix_database_init.sh`)**

**Features**:
- ✅ **Dependency installation**: Ensures all Python packages are installed
- ✅ **Database initialization**: Creates database with proper models
- ✅ **Verification**: Tests database connection and tables
- ✅ **Status reporting**: Shows current database status
- ✅ **Error handling**: Comprehensive error checking

## 🛠️ **Database Fix Script Features**

The `fix_database_init.sh` script provides:

### **Commands Available**
```bash
# Fix all database issues
sudo ./fix_database_init.sh fix

# Verify database is working
sudo ./fix_database_init.sh verify

# Show current database status
sudo ./fix_database_init.sh status

# Show help
sudo ./fix_database_init.sh help
```

### **What It Fixes**
- ✅ **Missing Dependencies**: Installs all required Python packages
- ✅ **Database Creation**: Creates SQLite database with all tables
- ✅ **Model Definitions**: Defines all database models (Item, Vendor, Customer, Order, etc.)
- ✅ **Initial Data**: Creates default printer and sync status records
- ✅ **Verification**: Tests database connection and table creation

## 🔍 **Database Models Created**

The initialization script creates these tables:

### **Core Tables**
- **`item`**: Product inventory items
- **`vendor`**: Supplier information
- **`customer`**: Customer information
- **`order`**: Sales orders
- **`order_item`**: Order line items
- **`lot`**: Inventory lots/batches
- **`printer`**: Label printer configuration

### **System Tables**
- **`sync_log`**: QuickBooks sync activity logs
- **`sync_status`**: Sync status and configuration

### **Initial Data Created**
- **Default Printer**: `Default Printer` at `192.168.1.100:9100`
- **Sync Status Records**: For customers, items, orders, and pricing sync

## 🚀 **Complete Fix Process**

### **Step 1: Fix Database Issues**
```bash
# Run the database fix script
sudo ./fix_database_init.sh fix
```

### **Step 2: Verify Database**
```bash
# Verify database is working
sudo ./fix_database_init.sh verify
```

### **Step 3: Continue VPS Setup**
```bash
# Re-run the VPS setup script
sudo ./vps_setup.sh
```

### **Step 4: Test the Application**
```bash
# Check if the service is running
sudo systemctl status label-printer

# Check if the application is accessible
curl http://localhost:5000/health
```

## 📊 **Expected Results**

After running the fix, you should see:

```bash
$ sudo ./fix_database_init.sh verify
[INFO] Verifying database...
[SUCCESS] Database file exists: /opt/label-printer/instance/inventory.db
[INFO] Database size: 12345 bytes
[INFO] Tables found: 9
[INFO]   - item
[INFO]   - vendor
[INFO]   - customer
[INFO]   - order
[INFO]   - order_item
[INFO]   - lot
[INFO]   - printer
[INFO]   - sync_log
[INFO]   - sync_status
[INFO] Database connection test successful
[SUCCESS] Database connection test passed
```

## 🔐 **Security Notes**

### **Database Security**
- ✅ **File Permissions**: Database file owned by `labelprinter:labelprinter`
- ✅ **Directory Permissions**: Instance directory has correct permissions
- ✅ **User Isolation**: Database operations run as dedicated user
- ✅ **SQLite Security**: Uses SQLite with proper file permissions

### **File Structure After Fix**
```
/opt/label-printer/
├── app.py                    # Main application
├── init_database.py         # Database initialization script
├── fix_database_init.sh     # Database fix script
├── venv/                    # Virtual environment
├── instance/                # Database directory (755)
│   └── inventory.db         # SQLite database (644)
└── logs/                    # Log directory
```

## 🔍 **Troubleshooting**

### **If You Still Get Import Errors**

1. **Check virtual environment**:
   ```bash
   sudo -u labelprinter -H bash -c "cd /opt/label-printer && source venv/bin/activate && pip list"
   ```

2. **Check Python path**:
   ```bash
   sudo -u labelprinter -H bash -c "cd /opt/label-printer && source venv/bin/activate && python -c 'import sys; print(sys.path)'"
   ```

3. **Test imports manually**:
   ```bash
   sudo -u labelprinter -H bash -c "cd /opt/label-printer && source venv/bin/activate && python -c 'import requests; print(\"requests imported successfully\")'"
   ```

### **Common Issues and Solutions**

#### **Issue: "No module named 'requests'"**
```bash
# Install missing dependencies
sudo -u labelprinter -H bash -c "cd /opt/label-printer && source venv/bin/activate && pip install requests"
```

#### **Issue: "Database is locked"**
```bash
# Check for running processes
sudo lsof /opt/label-printer/instance/inventory.db

# Kill any processes using the database
sudo pkill -f "python.*app.py"
```

#### **Issue: "Permission denied on database file"**
```bash
# Fix database file permissions
sudo chown labelprinter:labelprinter /opt/label-printer/instance/inventory.db
sudo chmod 644 /opt/label-printer/instance/inventory.db
```

## 🎯 **Next Steps**

1. **Run the database fix script** on your VPS
2. **Verify database** is working correctly
3. **Re-run the VPS setup** script
4. **Test the application** is working
5. **Access the web interface** and test functionality

---

**The database initialization issue has been identified and fixed. The updated scripts will handle database setup correctly going forward!** 🚀
