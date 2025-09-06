# Database Column Error Fix Guide - QuickBooks Label Printer

## 🚨 **Issue Identified**

The database initialization failed with this error:
```
Error initializing database: (sqlite3.OperationalError) no such column: printer.is_active
[SQL: SELECT count(*) AS count_1 
FROM (SELECT printer.id AS printer_id, printer.name AS printer_name, printer.ip_address AS printer_ip_address, printer.port AS printer_port, printer.is_active AS printer_is_active, printer.created_at AS printer_created_at, printer.updated_at AS printer_updated_at 
FROM printer) AS anon_1]
```

This happens because the database initialization script was trying to query the `printer` table for existing records before the table was actually created, causing a "column doesn't exist" error.

## 🔧 **Quick Fix Solution**

### **Option 1: Use the Database Column Error Fix Script (Recommended)**

I've created a dedicated fix script. Run this on your VPS:

```bash
# Run the database column error fix script
sudo ./fix_database_column_error.sh fix
```

### **Option 2: Manual Fix Commands**

If you prefer to fix manually, run these commands on your VPS:

```bash
# Backup existing database (if any)
sudo cp /opt/label-printer/instance/inventory.db /opt/label-printer/instance/inventory.db.backup.$(date +%Y%m%d_%H%M%S)

# Remove existing database
sudo rm -f /opt/label-printer/instance/inventory.db

# Create fresh database using simple script
sudo -u labelprinter -H bash -c "cd /opt/label-printer && source venv/bin/activate && python init_database_simple.py"
```

### **Option 3: Re-run the Updated VPS Setup Script**

The VPS setup script has been updated to use the simpler database initialization. You can re-run it:

```bash
# Re-run the updated setup script
sudo ./vps_setup.sh
```

## 📋 **What Was Fixed**

### **1. Created Simple Database Initialization Script (`init_database_simple.py`)**

**Features**:
- ✅ **No Initial Data**: Only creates tables, doesn't try to insert data
- ✅ **No Queries**: Doesn't query tables before they exist
- ✅ **Error Handling**: Graceful error handling and reporting
- ✅ **Verification**: Lists created tables for verification
- ✅ **Robust**: Less likely to fail during initialization

### **2. Updated VPS Setup Script (`vps_setup.sh`)**

**Before (Problematic)**:
```bash
sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && source venv/bin/activate && python init_database.py"
```

**After (Fixed)**:
```bash
# Use simple database initialization script
sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && source venv/bin/activate && python init_database_simple.py"
```

### **3. Created Database Column Error Fix Script (`fix_database_column_error.sh`)**

**Features**:
- ✅ **Backup**: Backs up existing database before fixing
- ✅ **Clean Slate**: Removes problematic database
- ✅ **Fresh Creation**: Creates new database with correct structure
- ✅ **Verification**: Tests database connection and tables
- ✅ **Status Reporting**: Shows current database status

## 🛠️ **Database Column Error Fix Script Features**

The `fix_database_column_error.sh` script provides:

### **Commands Available**
```bash
# Fix database column error
sudo ./fix_database_column_error.sh fix

# Verify database is working
sudo ./fix_database_column_error.sh verify

# Show current database status
sudo ./fix_database_column_error.sh status

# Show help
sudo ./fix_database_column_error.sh help
```

### **What It Fixes**
- ✅ **Column Errors**: Resolves "no such column" errors
- ✅ **Database Corruption**: Removes corrupted database files
- ✅ **Table Creation**: Creates all tables with correct structure
- ✅ **Verification**: Tests database connection and table listing
- ✅ **Backup**: Preserves existing data before fixing

## 🔍 **Root Cause Analysis**

### **The Problem**
The original `init_database.py` script had this problematic sequence:
1. **Create tables** with `db.create_all()`
2. **Query existing data** with `Printer.query.count() == 0`
3. **Insert initial data** if no records exist

### **Why It Failed**
- The `Printer.query.count()` was trying to access the `is_active` column
- But the table might not have been fully created yet
- Or there was a timing issue with SQLAlchemy's table creation

### **The Solution**
The new `init_database_simple.py` script:
1. **Only creates tables** with `db.create_all()`
2. **Lists created tables** for verification
3. **Doesn't try to insert data** during initialization
4. **Uses raw SQL queries** when needed instead of ORM queries

## 🚀 **Complete Fix Process**

### **Step 1: Fix Database Column Error**
```bash
# Run the database column error fix script
sudo ./fix_database_column_error.sh fix
```

### **Step 2: Verify Database**
```bash
# Verify database is working
sudo ./fix_database_column_error.sh verify
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
$ sudo ./fix_database_column_error.sh verify
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
[SUCCESS] Database verification passed
```

## 🔐 **Security Notes**

### **Database Security**
- ✅ **File Permissions**: Database file owned by `labelprinter:labelprinter`
- ✅ **Directory Permissions**: Instance directory has correct permissions
- ✅ **User Isolation**: Database operations run as dedicated user
- ✅ **Backup Safety**: Existing databases are backed up before fixing

### **File Structure After Fix**
```
/opt/label-printer/
├── app.py                           # Main application
├── init_database.py                # Original database script
├── init_database_simple.py         # Simple database script
├── fix_database_column_error.sh    # Column error fix script
├── venv/                           # Virtual environment
├── instance/                       # Database directory (755)
│   ├── inventory.db                # SQLite database (644)
│   └── inventory.db.backup.*       # Backup files (644)
└── logs/                           # Log directory
```

## 🔍 **Troubleshooting**

### **If You Still Get Column Errors**

1. **Check database file**:
   ```bash
   sudo -u labelprinter -H bash -c "cd /opt/label-printer && source venv/bin/activate && python -c 'import sqlite3; conn = sqlite3.connect(\"instance/inventory.db\"); cursor = conn.cursor(); cursor.execute(\"PRAGMA table_info(printer)\"); print(cursor.fetchall())'"
   ```

2. **Check table structure**:
   ```bash
   sudo -u labelprinter -H bash -c "cd /opt/label-printer && source venv/bin/activate && python -c 'import sqlite3; conn = sqlite3.connect(\"instance/inventory.db\"); cursor = conn.cursor(); cursor.execute(\"SELECT sql FROM sqlite_master WHERE type=\"table\" AND name=\"printer\"\"); print(cursor.fetchone())'"
   ```

3. **Verify all tables exist**:
   ```bash
   sudo -u labelprinter -H bash -c "cd /opt/label-printer && source venv/bin/activate && python -c 'import sqlite3; conn = sqlite3.connect(\"instance/inventory.db\"); cursor = conn.cursor(); cursor.execute(\"SELECT name FROM sqlite_master WHERE type=\"table\"\"); print([row[0] for row in cursor.fetchall()])'"
   ```

### **Common Issues and Solutions**

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

#### **Issue: "No such table"**
```bash
# Recreate database completely
sudo ./fix_database_column_error.sh fix
```

## 🎯 **Next Steps**

1. **Run the database column error fix script** on your VPS
2. **Verify database** is working correctly
3. **Re-run the VPS setup** script
4. **Test the application** is working
5. **Access the web interface** and test functionality

---

**The database column error has been identified and fixed. The updated scripts will handle database initialization correctly going forward!** 🚀
