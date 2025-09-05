# VPS Deployment Package - QuickBooks Label Printer

## 🚀 **Complete VPS Deployment Solution**

I've created a comprehensive VPS deployment package for your QuickBooks Label Printer system. Here's what's included:

### **📁 Files Created**

1. **`vps_setup.sh`** - Complete automated setup script
2. **`config_production.py`** - Production-optimized configuration
3. **`gunicorn.conf.py`** - Gunicorn WSGI server configuration
4. **`label-printer.service`** - Systemd service file
5. **`requirements-production.txt`** - Production dependencies
6. **`DEPLOYMENT_GUIDE.md`** - Comprehensive deployment guide
7. **`curl-format.txt`** - Performance testing format
8. **`VPS_DEPLOYMENT_SUMMARY.md`** - This summary

## 🎯 **One-Command Deployment**

### **Option 1: Direct from Git (Recommended)**
```bash
# Download and run setup script directly
curl -fsSL https://raw.githubusercontent.com/yourusername/label-printer/main/vps_setup.sh | bash
```

### **Option 2: Manual Setup**
```bash
# Clone repository
git clone https://github.com/yourusername/label-printer.git
cd label-printer

# Run setup script
./vps_setup.sh
```

## ⚡ **What the Setup Script Does**

### **System Setup**
- ✅ Updates Ubuntu packages
- ✅ Installs Python 3, Nginx, dependencies
- ✅ Creates dedicated `labelprinter` user
- ✅ Sets up application directory (`/opt/label-printer`)

### **Application Setup**
- ✅ Clones from your Git repository
- ✅ Creates Python virtual environment
- ✅ Installs production dependencies
- ✅ Initializes database
- ✅ Sets up file permissions

### **Service Configuration**
- ✅ Creates systemd service
- ✅ Configures Gunicorn WSGI server
- ✅ Sets up Nginx reverse proxy
- ✅ Configures SSL with Let's Encrypt
- ✅ Sets up firewall (UFW)

### **Production Features**
- ✅ Automatic backups (daily)
- ✅ Log rotation
- ✅ Performance monitoring
- ✅ Security hardening
- ✅ Error handling
- ✅ Health checks

## 🔧 **Production Configuration**

### **Optimized for 4-Core VPS**
- **Gunicorn**: 4 workers + 2 threads each = 8 concurrent requests
- **Nginx**: Reverse proxy with compression and caching
- **Database**: SQLite with connection pooling
- **Memory**: 200MB limit per worker
- **Security**: Firewall, SSL, security headers

### **Performance Features**
- **Caching**: LRU cache for sync status
- **Compression**: Gzip compression enabled
- **Static Files**: Optimized serving with caching
- **Database**: Connection pooling and optimization
- **Monitoring**: Request/response logging

## 🌐 **Access Information**

### **After Setup**
- **Web Interface**: `http://your-vps-ip` or `https://yourdomain.com`
- **Admin Login**: `/admin/login`
- **API Endpoints**: `/api/*`
- **Health Check**: `/health`

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

## 🔒 **Security Features**

### **System Security**
- ✅ UFW firewall configured
- ✅ SSH access only
- ✅ Non-root application user
- ✅ File permission restrictions
- ✅ Process isolation

### **Application Security**
- ✅ HTTPS enforcement
- ✅ Security headers
- ✅ CSRF protection
- ✅ Input validation
- ✅ Rate limiting
- ✅ Session security

### **Data Security**
- ✅ Encrypted backups
- ✅ Secure file uploads
- ✅ Database protection
- ✅ Log security
- ✅ Access logging

## 📊 **Monitoring & Maintenance**

### **Built-in Monitoring**
- **System Resources**: CPU, memory, disk usage
- **Application Performance**: Response times, error rates
- **Database Performance**: Query times, connection pool
- **Network**: Request/response monitoring
- **Logs**: Centralized logging with rotation

### **Automatic Maintenance**
- **Daily Backups**: 2 AM daily, 30-day retention
- **Log Rotation**: Automatic log cleanup
- **Database Maintenance**: Regular optimization
- **Security Updates**: Automated package updates
- **SSL Renewal**: Automatic certificate renewal

## 🚀 **Performance Optimizations**

### **Application Level**
- **Caching**: LRU cache for frequently accessed data
- **Database**: Optimized queries with connection pooling
- **Static Files**: Nginx serving with compression
- **Session Management**: Efficient session storage
- **Error Handling**: Graceful error recovery

### **System Level**
- **Gunicorn**: Multi-worker configuration
- **Nginx**: Reverse proxy with optimization
- **Database**: SQLite with proper indexing
- **Memory**: Efficient memory usage
- **CPU**: Multi-core utilization

## 📈 **Scaling Options**

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

## 🔧 **Configuration Options**

### **Environment Variables**
```bash
# QuickBooks API
QB_CLIENT_ID=your_client_id
QB_CLIENT_SECRET=your_client_secret
QB_COMPANY_ID=your_company_id

# Security
SECRET_KEY=your-secret-key
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=your_password

# Database
DATABASE_URI=sqlite:///instance/inventory.db

# Email (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

### **Production Settings**
- **Debug Mode**: Disabled
- **SSL**: Enabled with Let's Encrypt
- **Compression**: Gzip enabled
- **Caching**: Enabled
- **Monitoring**: Full logging
- **Security**: Hardened configuration

## 📞 **Support & Troubleshooting**

### **Common Commands**
```bash
# Check service status
sudo systemctl status label-printer

# View application logs
sudo journalctl -u label-printer -f

# Test Nginx configuration
sudo nginx -t

# Restart services
sudo systemctl restart label-printer nginx

# Check system resources
htop
free -h
df -h
```

### **Log Locations**
- **Application**: `/opt/label-printer/logs/`
- **System**: `/var/log/`
- **Nginx**: `/var/log/nginx/`
- **Service**: `sudo journalctl -u label-printer`

### **Configuration Files**
- **Application**: `/opt/label-printer/`
- **Nginx**: `/etc/nginx/sites-available/label-printer`
- **Systemd**: `/etc/systemd/system/label-printer.service`
- **Environment**: `/opt/label-printer/.env`

## 🎉 **Ready for Production**

### **What's Included**
- ✅ Complete automated setup
- ✅ Production-optimized configuration
- ✅ Security hardening
- ✅ Performance optimization
- ✅ Monitoring and logging
- ✅ Backup and recovery
- ✅ SSL/HTTPS support
- ✅ Firewall configuration
- ✅ Service management
- ✅ Comprehensive documentation

### **Next Steps**
1. **Update Git Repository**: Add these files to your repo
2. **Update Repository URL**: Change `GIT_REPO` in `vps_setup.sh`
3. **Deploy to VPS**: Run the setup script
4. **Configure Domain**: Set up DNS and SSL
5. **Test System**: Verify all functionality
6. **Monitor**: Set up monitoring and alerts

---

**Your QuickBooks Label Printer system is now ready for production deployment on any Ubuntu VPS!** 🚀

The setup script handles everything automatically, from system configuration to security hardening, making deployment as simple as running one command.
