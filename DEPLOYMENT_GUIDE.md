# QuickBooks Label Printer - VPS Deployment Guide

Complete guide for deploying the QuickBooks Label Printer system on an Ubuntu VPS.

## 🚀 **Quick Start**

### **1. Prerequisites**
- Ubuntu 20.04+ VPS with 4+ cores
- Root or sudo access
- Domain name (optional, for SSL)
- Git repository access

### **2. One-Command Setup**
```bash
# Download and run the setup script
curl -fsSL https://raw.githubusercontent.com/yourusername/label-printer/main/vps_setup.sh | bash
```

### **3. Manual Setup**
```bash
# Clone the repository
git clone https://github.com/yourusername/label-printer.git
cd label-printer

# Make setup script executable
chmod +x vps_setup.sh

# Run setup script
./vps_setup.sh
```

## 📋 **Setup Script Features**

The `vps_setup.sh` script automatically:

- ✅ Updates system packages
- ✅ Installs Python 3, Nginx, and dependencies
- ✅ Creates dedicated application user
- ✅ Sets up Python virtual environment
- ✅ Configures systemd service
- ✅ Sets up Nginx reverse proxy
- ✅ Configures firewall (UFW)
- ✅ Sets up SSL with Let's Encrypt
- ✅ Creates backup system
- ✅ Configures monitoring
- ✅ Starts all services

## 🔧 **Configuration**

### **Environment Variables**
Create `/opt/label-printer/.env`:
```bash
# QuickBooks API
QB_CLIENT_ID=your_client_id
QB_CLIENT_SECRET=your_client_secret
QB_COMPANY_ID=your_company_id
QB_SANDBOX=true

# Security
SECRET_KEY=your-super-secret-key
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=your_admin_password

# Database
DATABASE_URI=sqlite:///instance/inventory.db

# Email (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

### **Production Configuration**
The system uses `config_production.py` for production settings:
- Optimized for 4-core VPS
- Security headers enabled
- Performance tuning applied
- Error handling configured
- Monitoring enabled

## 🌐 **Nginx Configuration**

### **Basic HTTP Setup**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **SSL Setup**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔒 **Security Configuration**

### **Firewall Setup**
```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

### **SSL/TLS Configuration**
- Let's Encrypt certificates
- HTTP to HTTPS redirect
- Security headers
- HSTS enabled
- Perfect Forward Secrecy

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

# Application metrics
curl http://localhost:5002/health
```

## 🔄 **Backup & Recovery**

### **Automatic Backups**
- Daily backups at 2 AM
- 30-day retention
- Database and files included
- Compressed storage

### **Manual Backup**
```bash
# Run backup script
sudo -u labelprinter /opt/label-printer/backup.sh

# Restore from backup
cd /opt/label-printer
tar -xzf /opt/backups/label-printer/backup_YYYYMMDD_HHMMSS.tar.gz
```

### **Database Backup**
```bash
# SQLite backup
sqlite3 /opt/label-printer/instance/inventory.db ".backup /opt/backups/db_backup.db"

# Restore database
sqlite3 /opt/label-printer/instance/inventory.db < /opt/backups/db_backup.db
```

## 🚀 **Performance Optimization**

### **Gunicorn Configuration**
- 4 worker processes (matches VPS cores)
- 2 threads per worker
- 1000 worker connections
- 30-second timeout
- Memory limit: 200MB per worker

### **Nginx Optimization**
- Gzip compression enabled
- Static file caching
- Client max body size: 16MB
- Connection keep-alive
- Buffer optimization

### **Database Optimization**
- Connection pooling
- Query optimization
- Index optimization
- Regular maintenance

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
sudo systemctl restart nginx
```

### **Log Rotation**
```bash
# Check log rotation
sudo logrotate -d /etc/logrotate.d/label-printer

# Force log rotation
sudo logrotate -f /etc/logrotate.d/label-printer
```

### **Database Maintenance**
```bash
# SQLite maintenance
sqlite3 /opt/label-printer/instance/inventory.db "VACUUM;"
sqlite3 /opt/label-printer/instance/inventory.db "ANALYZE;"
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

#### **Database Issues**
```bash
# Check database file
ls -la /opt/label-printer/instance/inventory.db

# Check permissions
sudo -u labelprinter sqlite3 /opt/label-printer/instance/inventory.db ".tables"
```

#### **QuickBooks API Issues**
```bash
# Check API credentials
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://sandbox-quickbooks.api.intuit.com/v3/company/YOUR_COMPANY_ID/companyinfo/YOUR_COMPANY_ID"

# Check logs
sudo journalctl -u label-printer | grep -i quickbooks
```

### **Performance Issues**
```bash
# Check system resources
htop
free -h
df -h

# Check application performance
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:5002/"

# Check database performance
sqlite3 /opt/label-printer/instance/inventory.db "EXPLAIN QUERY PLAN SELECT * FROM items;"
```

## 📈 **Scaling**

### **Horizontal Scaling**
- Load balancer (HAProxy/Nginx)
- Multiple application instances
- Database clustering
- Redis for session storage

### **Vertical Scaling**
- Increase VPS resources
- Optimize database queries
- Add caching layer
- Use CDN for static files

## 🔐 **Security Best Practices**

### **System Security**
- Regular security updates
- Firewall configuration
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

### **Logs Location**
- Application logs: `/opt/label-printer/logs/`
- System logs: `/var/log/`
- Nginx logs: `/var/log/nginx/`
- Service logs: `sudo journalctl -u label-printer`

### **Configuration Files**
- Application: `/opt/label-printer/`
- Nginx: `/etc/nginx/sites-available/label-printer`
- Systemd: `/etc/systemd/system/label-printer.service`
- Environment: `/opt/label-printer/.env`

### **Useful Commands**
```bash
# Restart application
sudo systemctl restart label-printer

# Check service status
sudo systemctl status label-printer

# View real-time logs
sudo journalctl -u label-printer -f

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Check disk usage
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep label-printer
```

---

**The QuickBooks Label Printer system is now production-ready on your VPS!** 🚀
