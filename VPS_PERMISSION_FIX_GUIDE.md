# VPS Permission Fix Guide - QuickBooks Label Printer

## 🚨 **Issue Identified**

The VPS setup script encountered a permission error:
```
[INFO] Cloning repository...
main: line 125: cd: /opt/label-printer: Permission denied
```

This happens because the script tries to change to the `/opt/label-printer` directory before it's properly created and owned by the correct user.

## 🔧 **Quick Fix Solution**

### **Option 1: Use the Permission Fix Script (Recommended)**

I've created a dedicated fix script. Run this on your VPS:

```bash
# Download and run the fix script
sudo ./fix_vps_permissions.sh fix
```

### **Option 2: Manual Fix Commands**

If you prefer to fix manually, run these commands on your VPS:

```bash
# Create the directory with correct ownership
sudo mkdir -p /opt/label-printer
sudo chown labelprinter:labelprinter /opt/label-printer
sudo chmod 755 /opt/label-printer

# Verify the fix
sudo -u labelprinter test -r /opt/label-printer && echo "Read access: OK" || echo "Read access: FAILED"
sudo -u labelprinter test -w /opt/label-printer && echo "Write access: OK" || echo "Write access: FAILED"
```

### **Option 3: Re-run the Updated VPS Setup Script**

The VPS setup script has been updated to handle permissions correctly. You can re-run it:

```bash
# Re-run the updated setup script
sudo ./vps_setup.sh
```

## 📋 **What Was Fixed**

### **Updated VPS Setup Script (`vps_setup.sh`)**

**Before (Problematic)**:
```bash
cd "$APP_DIR"  # This failed because user couldn't access directory
sudo -u "$APP_USER" git clone "$GIT_REPO" .
```

**After (Fixed)**:
```bash
# Ensure directory exists with correct permissions
if [ ! -d "$APP_DIR" ]; then
    sudo mkdir -p "$APP_DIR"
    sudo chown "$APP_USER:$APP_USER" "$APP_DIR"
fi

# Use proper sudo with home directory and working directory
sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && git clone '$GIT_REPO' ."
```

### **Key Changes Made**

1. **Directory Creation**: Script now creates `/opt/label-printer` with correct ownership before trying to access it
2. **Proper sudo Usage**: Added `-H` flag to preserve home directory and used `bash -c` with explicit directory changes
3. **Permission Handling**: All operations now run with proper user context
4. **Error Prevention**: Added checks to ensure directories exist before operations

## 🛠️ **Permission Fix Script Features**

The `fix_vps_permissions.sh` script provides:

### **Commands Available**
```bash
# Fix all permission issues
sudo ./fix_vps_permissions.sh fix

# Verify permissions are correct
sudo ./fix_vps_permissions.sh verify

# Show current status
sudo ./fix_vps_permissions.sh status

# Show help
sudo ./fix_vps_permissions.sh help
```

### **What It Fixes**
- ✅ **Directory Ownership**: Sets `/opt/label-printer` to `labelprinter:labelprinter`
- ✅ **Directory Permissions**: Sets correct read/write/execute permissions
- ✅ **File Permissions**: Makes scripts executable, sets proper file permissions
- ✅ **Subdirectory Permissions**: Fixes `instance/`, `venv/`, `logs/` directories
- ✅ **Verification**: Tests that the user can actually access the directory

## 🔍 **Troubleshooting**

### **If You Still Get Permission Errors**

1. **Check if the user exists**:
   ```bash
   id labelprinter
   ```

2. **Check directory ownership**:
   ```bash
   ls -la /opt/
   ```

3. **Check directory permissions**:
   ```bash
   ls -la /opt/label-printer
   ```

4. **Test user access**:
   ```bash
   sudo -u labelprinter ls -la /opt/label-printer
   ```

### **Common Issues and Solutions**

#### **Issue: "labelprinter user does not exist"**
```bash
# Create the user
sudo useradd -r -s /bin/bash -d /opt/label-printer -m labelprinter
```

#### **Issue: "Directory exists but wrong ownership"**
```bash
# Fix ownership
sudo chown -R labelprinter:labelprinter /opt/label-printer
```

#### **Issue: "Permission denied on subdirectories"**
```bash
# Fix all subdirectories
sudo find /opt/label-printer -type d -exec chmod 755 {} \;
sudo find /opt/label-printer -type f -exec chmod 644 {} \;
```

## 🚀 **Complete VPS Setup Process**

### **Step 1: Fix Permissions**
```bash
# Run the permission fix script
sudo ./fix_vps_permissions.sh fix
```

### **Step 2: Verify Fix**
```bash
# Verify permissions are correct
sudo ./fix_vps_permissions.sh verify
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
$ sudo ./fix_vps_permissions.sh verify
[INFO] Verifying permissions...
[SUCCESS] Directory ownership is correct: labelprinter:labelprinter
[SUCCESS] User labelprinter can read the directory
[SUCCESS] User labelprinter can write to the directory
[SUCCESS] Permission verification complete
```

## 🔐 **Security Notes**

### **Why This Approach is Secure**
- ✅ **Principle of Least Privilege**: Application runs as dedicated `labelprinter` user
- ✅ **Proper Ownership**: All files owned by the application user
- ✅ **Minimal Permissions**: Only necessary permissions granted
- ✅ **No Root Access**: Application never runs as root

### **Directory Structure After Fix**
```
/opt/label-printer/
├── app.py                    # Main application (644)
├── vps_setup.sh             # Setup script (755)
├── update_system.sh         # Update script (755)
├── fix_vps_permissions.sh   # Fix script (755)
├── venv/                    # Virtual environment (755)
├── instance/                # Database directory (755)
│   └── inventory.db         # Database file (644)
└── logs/                    # Log directory (755)
```

## 🎯 **Next Steps**

1. **Run the fix script** on your VPS
2. **Verify permissions** are correct
3. **Re-run the VPS setup** script
4. **Test the application** is working
5. **Access the web interface** and test functionality

---

**The permission issue has been identified and fixed. The updated scripts will handle permissions correctly going forward!** 🚀
