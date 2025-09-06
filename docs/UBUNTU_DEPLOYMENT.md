# Ubuntu VPS Deployment Guide

This guide will help you deploy the Label Printer application on an Ubuntu VPS with 4 cores, optimized for production use.

## 🚀 Quick Start

### Prerequisites
- Ubuntu 20.04+ VPS with 4 cores
- Root or sudo access
- At least 2GB RAM
- 20GB+ disk space

### One-Command Deployment
```bash
# Download and run the deployment script
curl -fsSL https://your-repo.com/deploy_ubuntu.sh | sudo bash
```

### Manual Deployment
```bash
# 1. Clone or upload your application
git clone <your-repo> /opt/label-printer
cd /opt/label-printer

# 2. Run the deployment script
sudo chmod +x deploy_ubuntu.sh
sudo ./deploy_ubuntu.sh

# 3. Start the application
sudo ./start_production.sh
```

## 📋 System Architecture

### Components
- **Nginx**: Reverse proxy and load balancer
- **Gunicorn**: WSGI server with 4 workers (matching your cores)
- **Redis**: Caching and session storage
- **SQLite**: Database (can be upgraded to PostgreSQL)
- **Systemd**: Service management

### Port Configuration
- **Port 80**: Nginx (HTTP)
- **Port 443**: Nginx (HTTPS - configure SSL)
- **Port 8000**: Gunicorn (internal)
- **Port 6379**: Redis (internal)

## ⚙️ Configuration Files

### Production Configuration
- `config_production.py`: Production settings optimized for 4 cores
- `gunicorn.conf.py`: Gunicorn configuration with 4 workers
- `nginx.conf`: Nginx reverse proxy configuration
- `label-printer.service`: Systemd service file

### Key Optimizations
- **4 Gunicorn workers** (matching your core count)
- **Connection pooling** for database efficiency
- **Redis caching** for improved performance
- **Rate limiting** to prevent abuse
- **Gzip compression** for faster responses
- **Security headers** for protection

## 🔧 Management Commands

### Service Management
```bash
# Start services
sudo systemctl start label-printer
sudo systemctl start nginx
sudo systemctl start redis-server

# Stop services
sudo systemctl stop label-printer

# Restart services
sudo systemctl restart label-printer

# Check status
sudo systemctl status label-printer
```

### Monitoring
```bash
# Run system monitor
sudo ./monitor.sh

# View logs
sudo journalctl -u label-printer -f
sudo tail -f /var/log/label-printer/gunicorn_error.log

# Check application health
curl http://localhost:8000/health
```

### Database Backup
```bash
# Manual backup
sudo ./backup.sh

# Schedule automatic backups (add to crontab)
sudo crontab -e
# Add: 0 2 * * * /opt/label-printer/backup.sh
```

## 📊 Performance Tuning

### For 4-Core VPS
- **Workers**: 4 Gunicorn workers (1 per core)
- **Connections**: 1000 per worker
- **Memory**: ~512MB per worker
- **Timeout**: 120 seconds

### Database Optimization
```python
# In config_production.py
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_TIMEOUT = 30
DB_POOL_RECYCLE = 3600
```

### Redis Configuration
```bash
# Edit /etc/redis/redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

## 🔒 Security Configuration

### Firewall Setup
```bash
# Configure UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
```

### SSL Configuration
1. Obtain SSL certificates (Let's Encrypt recommended)
2. Update `nginx.conf` with SSL settings
3. Redirect HTTP to HTTPS

### Security Headers
The Nginx configuration includes:
- X-Frame-Options
- X-XSS-Protection
- X-Content-Type-Options
- Content-Security-Policy

## 📈 Monitoring and Logging

### Log Locations
- Application logs: `/var/log/label-printer/`
- Nginx logs: `/var/log/nginx/`
- System logs: `journalctl -u label-printer`

### Health Checks
- Application: `http://your-domain/health`
- Database connectivity
- Redis connectivity
- System resources

### Performance Monitoring
```bash
# Real-time monitoring
htop
sudo ./monitor.sh

# Log analysis
sudo tail -f /var/log/label-printer/gunicorn_access.log
```

## 🔄 Updates and Maintenance

### Application Updates
```bash
cd /opt/label-printer
git pull origin main
sudo systemctl restart label-printer
```

### System Updates
```bash
sudo apt update && sudo apt upgrade -y
sudo systemctl restart label-printer nginx redis-server
```

### Database Maintenance
```bash
# Check database integrity
sqlite3 /opt/label-printer/instance/inventory.db "PRAGMA integrity_check;"

# Optimize database
sqlite3 /opt/label-printer/instance/inventory.db "VACUUM;"
```

## 🚨 Troubleshooting

### Common Issues

#### Application Not Starting
```bash
# Check logs
sudo journalctl -u label-printer -f

# Check configuration
sudo nginx -t
```

#### High Memory Usage
```bash
# Check worker processes
ps aux | grep gunicorn

# Restart if needed
sudo systemctl restart label-printer
```

#### Database Issues
```bash
# Check database file
ls -la /opt/label-printer/instance/inventory.db

# Restore from backup
sudo cp /opt/backups/label-printer/inventory_backup_YYYYMMDD_HHMMSS.db.gz /opt/label-printer/instance/inventory.db.gz
sudo gunzip /opt/label-printer/instance/inventory.db.gz
```

### Performance Issues
1. Check system resources: `htop`
2. Monitor logs for errors
3. Verify database integrity
4. Check network connectivity
5. Review rate limiting settings

## 📞 Support

### Useful Commands
```bash
# Service status
sudo systemctl status label-printer nginx redis-server

# Application health
curl -s http://localhost:8000/health | python3 -m json.tool

# System resources
free -h && df -h

# Network connections
netstat -tuln | grep -E ":(80|443|8000|6379)"
```

### Log Analysis
```bash
# Recent errors
sudo journalctl -u label-printer --since "1 hour ago" | grep -i error

# Access patterns
sudo tail -100 /var/log/label-printer/gunicorn_access.log | grep -E "(GET|POST)"
```

## 🎯 Optimization Checklist

- [ ] 4 Gunicorn workers configured
- [ ] Redis caching enabled
- [ ] Database connection pooling optimized
- [ ] Nginx reverse proxy configured
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Monitoring scripts deployed
- [ ] Backup system configured
- [ ] Log rotation enabled
- [ ] Security headers configured

## 📚 Additional Resources

- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)
- [Redis Configuration](https://redis.io/docs/manual/config/)
- [Systemd Service Management](https://systemd.io/)
- [Ubuntu Security Guide](https://ubuntu.com/security)

---

**Note**: This deployment is optimized for a 4-core Ubuntu VPS. Adjust worker counts and resource limits based on your specific hardware configuration.
