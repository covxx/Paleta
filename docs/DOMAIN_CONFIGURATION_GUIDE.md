# 🌐 Domain Configuration Guide - ProduceFlow

This guide explains how to configure a domain name for your ProduceFlow application on a VPS.

## 📋 Prerequisites

- ProduceFlow application installed on VPS
- Domain name registered with a domain registrar
- Access to your domain's DNS settings
- Root/sudo access on the VPS

## 🚀 Quick Setup

### Option 1: During Initial Installation

When running the VPS setup script, you'll be prompted for a domain name:

```bash
sudo ./vps_setup.sh
```

The script will ask:
```
Enter your domain name (or press Enter to skip): yourdomain.com
```

### Option 2: Configure Domain After Installation

If you didn't configure a domain during installation, use the domain configuration script:

```bash
sudo ./scripts/configure_domain.sh --configure
```

## 🔧 Manual Configuration

### Step 1: DNS Configuration

1. **Log into your domain registrar** (GoDaddy, Namecheap, Cloudflare, etc.)
2. **Navigate to DNS management**
3. **Create/Update A record:**
   - **Type**: A
   - **Name**: @ (or leave blank for root domain)
   - **Value**: Your VPS IP address
   - **TTL**: 300 (5 minutes) or default

4. **Create/Update WWW record:**
   - **Type**: A
   - **Name**: www
   - **Value**: Your VPS IP address
   - **TTL**: 300 (5 minutes) or default

### Step 2: Update Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/produceflow
```

Update the server_name line:
```nginx
server_name yourdomain.com www.yourdomain.com;
```

Test and reload Nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 🛠️ Domain Configuration Script

The `configure_domain.sh` script provides several options:

### Configure Domain
```bash
sudo ./scripts/configure_domain.sh --configure
```

### Show Current Configuration
```bash
sudo ./scripts/configure_domain.sh --show
```

### Remove Domain Configuration
```bash
sudo ./scripts/configure_domain.sh --remove
```

### Show Help
```bash
sudo ./scripts/configure_domain.sh --help
```

## 🔍 Verification

### Check DNS Propagation
```bash
# Check if DNS is pointing to your server
nslookup yourdomain.com
dig yourdomain.com

# Check from your server
curl -s ifconfig.me  # This should match your DNS A record
```

### Test Domain Access
```bash
# Test HTTP access
curl -I http://yourdomain.com

# Test from browser
# Visit: http://yourdomain.com
```

## 🔒 SSL Certificate Setup

After configuring your domain, set up SSL:

```bash
sudo ./scripts/setup_ssl.sh -d yourdomain.com -e admin@yourdomain.com
```

## 📊 Troubleshooting

### Common Issues

#### 1. DNS Not Propagated
**Symptoms**: Domain shows old IP or doesn't resolve
**Solution**: 
- Wait 5-30 minutes for DNS propagation
- Check DNS with: `nslookup yourdomain.com`
- Verify A record points to correct IP

#### 2. Nginx Configuration Error
**Symptoms**: `nginx -t` fails
**Solution**:
```bash
sudo nginx -t  # Check for syntax errors
sudo nano /etc/nginx/sites-available/produceflow  # Fix configuration
sudo systemctl reload nginx
```

#### 3. Domain Not Accessible
**Symptoms**: Connection refused or timeout
**Solution**:
- Check firewall: `sudo ufw status`
- Check Nginx status: `sudo systemctl status nginx`
- Check application status: `sudo systemctl status produceflow`

#### 4. SSL Certificate Issues
**Symptoms**: SSL setup fails
**Solution**:
- Ensure domain resolves to your server
- Check port 80 is open: `sudo ufw allow 80`
- Check port 443 is open: `sudo ufw allow 443`

### Debug Commands

```bash
# Check server IP
curl -s ifconfig.me

# Check DNS resolution
nslookup yourdomain.com
dig yourdomain.com

# Check Nginx configuration
sudo nginx -t

# Check service status
sudo systemctl status nginx
sudo systemctl status produceflow

# Check firewall
sudo ufw status

# Check logs
sudo journalctl -u nginx -f
sudo journalctl -u produceflow -f
```

## 🌍 Multiple Domains

To configure multiple domains for the same application:

```nginx
server_name domain1.com www.domain1.com domain2.com www.domain2.com;
```

## 📝 Configuration Files

### Nginx Configuration
- **File**: `/etc/nginx/sites-available/produceflow`
- **Key setting**: `server_name yourdomain.com www.yourdomain.com;`

### Systemd Service
- **File**: `/etc/systemd/system/produceflow.service`
- **No domain-specific settings needed**

## 🔄 Updates and Maintenance

### Update Domain
```bash
sudo ./scripts/configure_domain.sh --configure
```

### Remove Domain
```bash
sudo ./scripts/configure_domain.sh --remove
```

### Check Configuration
```bash
sudo ./scripts/configure_domain.sh --show
```

## 📞 Support

If you encounter issues:

1. **Check logs**: `sudo journalctl -u produceflow -f`
2. **Verify DNS**: `nslookup yourdomain.com`
3. **Test connectivity**: `curl -I http://yourdomain.com`
4. **Check firewall**: `sudo ufw status`

## 🎯 Best Practices

1. **Use HTTPS**: Always set up SSL certificates
2. **Monitor DNS**: Use tools like DNS checker
3. **Backup configs**: Keep copies of working configurations
4. **Test thoroughly**: Verify all functionality after changes
5. **Document changes**: Keep track of configuration modifications

---

**Your ProduceFlow application is now accessible via your domain name!** 🚀




