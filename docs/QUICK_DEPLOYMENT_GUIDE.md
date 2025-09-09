# Quick Deployment Guide - app.srjlabs.dev

Quick reference guide for deploying the QuickBooks Label Printer to your VPS with the domain `app.srjlabs.dev`.

## 🚀 **One-Command Deployment**

### **Prerequisites**
- Ubuntu 20.04+ VPS with 4+ cores
- Root or sudo access
- Domain `app.srjlabs.dev` pointing to your VPS IP
- Ports 80 and 443 open

### **Deploy Everything**
```bash
# Download and run the complete deployment script
curl -fsSL https://raw.githubusercontent.com/covxx/Paleta/refs/heads/master/scripts/deploy_production.sh | sudo bash
```

### **Manual Deployment**
```bash
# Clone repository
git clone https://github.com/covxx/Paleta.git
cd Paleta

# Run deployment script
sudo ./scripts/deploy_production.sh -d app.srjlabs.dev -e admin@srjlabs.dev
```

## 📋 **What Gets Installed**

### **System Components**
- ✅ Python 3 + virtual environment
- ✅ Nginx reverse proxy
- ✅ Gunicorn WSGI server (4 workers)
- ✅ SQLite database
- ✅ Systemd service
- ✅ UFW firewall
- ✅ Let's Encrypt SSL

### **Application Features**
- ✅ QuickBooks integration
- ✅ Label printing
- ✅ Order management
- ✅ Customer management
- ✅ Inventory tracking
- ✅ Admin interface
- ✅ API endpoints

## 🔧 **Configuration**

### **Environment Variables**
Create `/opt/label-printer/.env`:
```bash
# QuickBooks API
QB_CLIENT_ID=your_client_id
QB_CLIENT_SECRET=your_client_secret
QB_COMPANY_ID=your_company_id
QB_SANDBOX=false

# Security
SECRET_KEY=your-super-secret-production-key
ADMIN_EMAIL=admin@srjlabs.dev
ADMIN_PASSWORD=your_secure_password

# Database
DATABASE_URI=sqlite:///instance/inventory.db
```

### **File Permissions**
```bash
sudo chown -R labelprinter:labelprinter /opt/label-printer
sudo chmod 600 /opt/label-printer/.env
```

## 🌐 **Access Your Application**

### **URLs**
- **Main App**: https://app.srjlabs.dev
- **Admin Panel**: https://app.srjlabs.dev/admin/login
- **API**: https://app.srjlabs.dev/api/
- **Health Check**: https://app.srjlabs.dev/health

### **Default Login**
- **Username**: admin@srjlabs.dev
- **Password**: (set in .env file)

## 🔧 **Service Management**

### **Application Service**
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

### **Nginx Service**
```bash
# Test Configuration
sudo nginx -t

# Reload Configuration
sudo systemctl reload nginx

# View Logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🔒 **SSL Management**

### **Certificate Status**
```bash
# View certificates
sudo certbot certificates

# Test renewal
sudo certbot renew --dry-run

# Manual renewal
sudo certbot renew
```

### **Automatic Renewal**
- ✅ Configured automatically
- ✅ Runs daily at 12 PM
- ✅ Logs to `/var/log/letsencrypt/`

## 📊 **Monitoring**

### **System Resources**
```bash
# CPU and Memory
htop

# Network Usage
nethogs

# Disk I/O
iotop

# Disk Space
df -h
```

### **Application Health**
```bash
# Health Check
curl -s https://app.srjlabs.dev/health | python3 -m json.tool

# Service Status
sudo systemctl status label-printer nginx
```

## 🔄 **Backup & Recovery**

### **Automatic Backups**
- ✅ Daily backups at 2 AM
- ✅ 30-day retention
- ✅ Stored in `/opt/backups/label-printer/`

### **Manual Backup**
```bash
sudo -u labelprinter /opt/label-printer/backup.sh
```

### **Restore from Backup**
```bash
cd /opt/label-printer
sudo -u labelprinter tar -xzf /opt/backups/label-printer/backup_YYYYMMDD_HHMMSS.tar.gz
sudo systemctl restart label-printer
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Service Won't Start**
```bash
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
```

#### **SSL Issues**
```bash
# Check certificate
sudo certbot certificates

# Test SSL
openssl s_client -connect app.srjlabs.dev:443 -servername app.srjlabs.dev
```

#### **Database Issues**
```bash
# Check database
ls -la /opt/label-printer/instance/inventory.db

# Test database
sudo -u labelprinter sqlite3 /opt/label-printer/instance/inventory.db ".tables"
```

## 🔄 **Updates**

### **Application Updates**
```bash
cd /opt/label-printer
sudo -u labelprinter git pull origin main
sudo -u labelprinter bash -c "source venv/bin/activate && pip install -r requirements.txt"
sudo systemctl restart label-printer
```

### **System Updates**
```bash
sudo apt update && sudo apt upgrade -y
sudo systemctl restart label-printer nginx
```

## 📞 **Support Commands**

### **Quick Status Check**
```bash
# All services
sudo systemctl status label-printer nginx

# Application health
curl -s https://app.srjlabs.dev/health

# System resources
htop
free -h
df -h
```

### **Log Analysis**
```bash
# Recent errors
sudo journalctl -u label-printer --since "1 hour ago" | grep -i error

# Nginx access
sudo tail -100 /var/log/nginx/access.log

# SSL logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

## 🎯 **Quick Checklist**

### **Before Deployment**
- [ ] VPS with Ubuntu 20.04+
- [ ] Root/sudo access
- [ ] Domain `app.srjlabs.dev` points to VPS IP
- [ ] Ports 80 and 443 open
- [ ] QuickBooks API credentials ready

### **After Deployment**
- [ ] Application accessible at https://app.srjlabs.dev
- [ ] SSL certificate valid
- [ ] Admin login working
- [ ] QuickBooks integration configured
- [ ] Backups scheduled
- [ ] Monitoring active

## 📚 **File Locations**

### **Configuration Files**
- **Application**: `/opt/label-printer/`
- **Nginx**: `/etc/nginx/sites-available/label-printer`
- **Systemd**: `/etc/systemd/system/label-printer.service`
- **SSL**: `/etc/letsencrypt/live/app.srjlabs.dev/`
- **Environment**: `/opt/label-printer/.env`

### **Log Files**
- **Application**: `sudo journalctl -u label-printer`
- **Nginx**: `/var/log/nginx/`
- **SSL**: `/var/log/letsencrypt/`
- **System**: `/var/log/`

### **Backup Files**
- **Location**: `/opt/backups/label-printer/`
- **Schedule**: Daily at 2 AM
- **Retention**: 30 days

---

**Your QuickBooks Label Printer is now running at https://app.srjlabs.dev!** 🚀

For detailed information, see the complete [VPS Production Deployment Guide](VPS_PRODUCTION_DEPLOYMENT_GUIDE.md).
