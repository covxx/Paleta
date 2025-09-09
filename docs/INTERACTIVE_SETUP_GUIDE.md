# 🚀 Interactive VPS Setup Guide - ProduceFlow

This guide explains how to use the interactive VPS setup script that configures domain names and installs the ProduceFlow application.

## 📋 Overview

The VPS setup script now includes **interactive domain configuration** that:
- Prompts for domain name during installation
- Validates domain name format
- Configures Nginx with the domain from the start
- Provides comprehensive installation summary
- Offers additional configuration options

## 🎯 Quick Start

### Run the Interactive Setup

```bash
sudo ./scripts/vps_setup.sh
```

The script will guide you through:
1. **Domain Configuration** - Enter your domain name
2. **Additional Options** - Choose SSL, email, backup settings
3. **Installation Summary** - Review configuration before installation
4. **Automatic Installation** - Full VPS setup with your domain

## 🌐 Domain Configuration

### Interactive Domain Setup

When you run the setup script, you'll see:

```
🌐 Domain Configuration
=======================

To access ProduceFlow via a domain name, you need to:
1. Point your domain's DNS A record to this server's IP address
2. Provide the domain name below

Current server IP: 192.168.1.100

Enter your domain name (e.g., mydomain.com) or press Enter to skip: 
```

### Domain Validation

The script validates domain names using regex:
- ✅ `mydomain.com` - Valid
- ✅ `subdomain.example.org` - Valid  
- ✅ `my-site.co.uk` - Valid
- ❌ `invalid` - Invalid (no TLD)
- ❌ `-invalid.com` - Invalid (starts with dash)

### Domain Confirmation

After entering a valid domain:
```
Domain configured: mydomain.com
Make sure your DNS A record points to: 192.168.1.100

Is this correct? (y/n): 
```

## 🔧 Additional Configuration

After domain setup, you'll see:

```
🔧 Additional Configuration
===========================

Would you like to configure additional options?

1. SSL Certificate (Let's Encrypt)
2. Email notifications  
3. Backup configuration
4. Skip additional configuration

Enter your choice (1-4):
```

### Options Explained

**1. SSL Certificate**
- Information about SSL setup after installation
- Command provided for later SSL configuration

**2. Email Notifications**
- Information about email configuration in admin panel

**3. Backup Configuration**
- Automatic backup setup information

**4. Skip Additional Configuration**
- Proceed with default settings

## 📋 Installation Summary

Before installation begins, you'll see:

```
📋 Installation Summary
=======================

Application: ProduceFlow
Installation Directory: /opt/produceflow
Service User: produceflow
Service Name: produceflow
Domain: mydomain.com
Access URL: http://mydomain.com

The installation will now begin...

Press Enter to continue or Ctrl+C to cancel:
```

## 🛠️ What Gets Configured

### With Domain Name

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name mydomain.com www.mydomain.com;
    # ... rest of configuration
}
```

**Systemd Service:**
```ini
[Unit]
Description=ProduceFlow
# ... service configuration
```

**Directory Structure:**
```
/opt/produceflow/
├── app.py
├── configs/
├── scripts/
├── static/
├── templates/
└── venv/
```

### Without Domain Name

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name _;  # Accept any domain
    # ... rest of configuration
}
```

## 🧪 Testing the Interactive Setup

### Test Script

Use the test script to try the interactive configuration without installation:

```bash
./scripts/test_interactive_setup.sh
```

This will:
- Test domain configuration prompts
- Validate domain name format
- Show installation summary
- **No actual installation performed**

### Test Output Example

```
ProduceFlow - Interactive Setup Test
====================================

[INFO] This is a test of the interactive domain configuration.
[INFO] No actual installation will be performed.

🌐 Domain Configuration
=======================

[INFO] To access ProduceFlow via a domain name, you need to:
[INFO] 1. Point your domain's DNS A record to this server's IP address
[INFO] 2. Provide the domain name below

[INFO] Current server IP: 192.168.1.100

Enter your domain name (e.g., mydomain.com) or press Enter to skip: mydomain.com
[INFO] Domain configured: mydomain.com
[INFO] Make sure your DNS A record points to: 192.168.1.100

Is this correct? (y/n): y

📋 Installation Summary
=======================

[INFO] Application: ProduceFlow
[INFO] Installation Directory: /opt/produceflow
[INFO] Service User: produceflow
[INFO] Service Name: produceflow
[INFO] Domain: mydomain.com
[INFO] Access URL: http://mydomain.com

[SUCCESS] Interactive setup test completed!
```

## 🔄 Post-Installation

### Domain Management

After installation, manage your domain:

```bash
# Show current configuration
sudo /opt/produceflow/scripts/configure_domain.sh --show

# Update domain
sudo /opt/produceflow/scripts/configure_domain.sh --configure

# Remove domain
sudo /opt/produceflow/scripts/configure_domain.sh --remove
```

### SSL Setup

If you configured a domain:

```bash
sudo /opt/produceflow/scripts/setup_ssl.sh -d mydomain.com -e admin@mydomain.com
```

## 🐛 Troubleshooting

### Common Issues

**1. Domain Validation Fails**
- Check domain format: `example.com`
- Ensure no leading/trailing spaces
- Use valid TLD (.com, .org, .net, etc.)

**2. DNS Not Pointing to Server**
- Verify A record points to server IP
- Wait for DNS propagation (5-30 minutes)
- Use `nslookup mydomain.com` to check

**3. Installation Fails**
- Check sudo permissions
- Ensure internet connectivity
- Review error messages in terminal

### Debug Commands

```bash
# Check server IP
curl -s ifconfig.me

# Check DNS resolution
nslookup mydomain.com

# Test nginx configuration
sudo nginx -t

# Check service status
sudo systemctl status produceflow
```

## 📚 Script Features

### Interactive Elements

- **Domain name validation** with regex
- **Confirmation prompts** for important settings
- **Installation summary** before proceeding
- **Progress indicators** during installation
- **Colored output** for better readability

### Error Handling

- **Input validation** for domain names
- **Graceful error messages** with suggestions
- **Rollback capability** on installation failure
- **Comprehensive logging** for debugging

### User Experience

- **Clear instructions** at each step
- **Helpful examples** for domain names
- **Progress feedback** during long operations
- **Final summary** with next steps

## 🎯 Best Practices

1. **Prepare DNS First**: Set up DNS A record before running script
2. **Test Domain**: Use test script to verify configuration
3. **Backup**: Take server snapshot before installation
4. **Monitor Logs**: Watch installation progress
5. **Verify Access**: Test domain access after installation

---

**The interactive setup makes domain configuration seamless and ensures your ProduceFlow application is accessible via your domain name from day one!** 🚀

