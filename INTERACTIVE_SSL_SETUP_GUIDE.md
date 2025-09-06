# Interactive SSL Setup Guide - QuickBooks Label Printer

## 🔒 **Enhanced SSL Integration with Interactive Prompts**

I've updated the VPS setup script to include interactive prompts for SSL configuration. Now the script will ask for domain name and email if they're not provided via command line arguments.

## 🚀 **How It Works**

### **Interactive SSL Configuration**

When you run the VPS setup script without SSL parameters, it will now prompt you:

```bash
sudo ./vps_setup.sh
```

**You'll see:**
```
[INFO] Starting QuickBooks Label Printer VPS Setup...

[INFO] SSL Certificate Configuration
==================================

[INFO] You can set up free SSL certificates using Let's Encrypt.
[INFO] This will enable HTTPS access to your application.

[WARNING] SSL Requirements:
[INFO]   - Domain name must point to this server's IP address
[INFO]   - Ports 80 and 443 must be open in firewall
[INFO]   - Email is used for Let's Encrypt notifications

Enter your domain name (e.g., yourdomain.com) or press Enter to skip SSL: 
```

### **Step-by-Step Process**

1. **Domain Name Prompt**
   - Enter your domain name (e.g., `yourdomain.com`)
   - Press Enter to skip SSL setup

2. **Email Prompt** (if domain provided)
   - Enter your email address for Let's Encrypt notifications
   - This email receives renewal notifications and warnings

3. **Domain Validation**
   - Script checks if domain points to your server's IP
   - Warns if domain configuration is incorrect
   - Asks if you want to continue anyway

4. **SSL Setup Confirmation**
   - Shows final SSL configuration
   - Proceeds with SSL setup if confirmed

## 📋 **Usage Examples**

### **Option 1: Interactive Setup (Recommended)**
```bash
# Run setup and answer prompts
sudo ./vps_setup.sh

# You'll be prompted for:
# - Domain name (e.g., yourdomain.com)
# - Email address (e.g., admin@yourdomain.com)
```

### **Option 2: Command Line Setup**
```bash
# Provide SSL parameters directly
sudo ./vps_setup.sh -d yourdomain.com -e admin@yourdomain.com
```

### **Option 3: Skip SSL Setup**
```bash
# Run setup without SSL
sudo ./vps_setup.sh

# When prompted for domain name, just press Enter
```

## 🔍 **Interactive Flow Example**

Here's what you'll see during the interactive setup:

```bash
$ sudo ./vps_setup.sh

[INFO] Starting QuickBooks Label Printer VPS Setup...

[INFO] SSL Certificate Configuration
==================================

[INFO] You can set up free SSL certificates using Let's Encrypt.
[INFO] This will enable HTTPS access to your application.

[WARNING] SSL Requirements:
[INFO]   - Domain name must point to this server's IP address
[INFO]   - Ports 80 and 443 must be open in firewall
[INFO]   - Email is used for Let's Encrypt notifications

Enter your domain name (e.g., yourdomain.com) or press Enter to skip SSL: yourdomain.com
Enter your email address for Let's Encrypt notifications: admin@yourdomain.com
[SUCCESS] SSL will be configured for domain: yourdomain.com
[SUCCESS] SSL email: admin@yourdomain.com
[INFO] Validating domain configuration...
[SUCCESS] Domain configuration looks good!

[INFO] Updating system packages...
[SUCCESS] System packages updated
[INFO] Installing required packages...
[SUCCESS] Required packages installed
...
[INFO] Setting up SSL with Let's Encrypt...
[SUCCESS] SSL certificate obtained and configured successfully!
[SUCCESS] SSL is working correctly!
[SUCCESS] Setup completed successfully!

Access Information:
  - Web Interface: https://yourdomain.com (SSL enabled)
  - HTTP Redirect: http://yourdomain.com (redirects to HTTPS)
  - Admin Login: /admin/login
```

## 🛠️ **Domain Validation Features**

### **Automatic Domain Check**
The script automatically validates your domain configuration:

1. **Gets Server IP**: Retrieves your server's public IP address
2. **Checks Domain Resolution**: Verifies domain points to your server
3. **Compares IPs**: Ensures domain and server IPs match
4. **Warns if Mismatch**: Alerts you if domain is misconfigured
5. **Asks for Confirmation**: Lets you continue anyway if needed

### **Domain Validation Example**
```bash
[INFO] Validating domain configuration...
[WARNING] Domain yourdomain.com does not resolve to this server's IP (192.168.1.100)
[WARNING] Current domain IP: 203.0.113.1
[INFO] Please update your DNS records before proceeding with SSL setup.

Continue with SSL setup anyway? (y/N): 
```

## 🔧 **SSL Requirements Check**

### **Prerequisites Validation**
The script checks for SSL requirements:

- ✅ **Domain Name**: Must be provided
- ✅ **Email Address**: Must be provided
- ✅ **Domain Resolution**: Must point to server IP
- ✅ **Ports Open**: Ports 80/443 must be accessible
- ✅ **Nginx Ready**: Nginx must be installed and running

### **Common Issues and Solutions**

#### **Issue: "Domain does not resolve to this server"**
```bash
# Check your domain's current IP
dig +short yourdomain.com

# Check your server's IP
curl -s ifconfig.me

# Update your DNS records to point to your server's IP
```

#### **Issue: "Ports 80/443 not accessible"**
```bash
# Check if ports are open
sudo ufw status
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Open ports if needed
sudo ufw allow 80
sudo ufw allow 443
```

## 📊 **SSL Configuration Options**

### **Interactive Prompts**
- **Domain Name**: `yourdomain.com`
- **Email Address**: `admin@yourdomain.com`
- **Domain Validation**: Automatic IP checking
- **Confirmation**: Option to continue despite warnings

### **Command Line Options**
- **`-d, --domain`**: Set domain name
- **`-e, --email`**: Set email address
- **`-h, --help`**: Show help message

### **Skip SSL Options**
- **Press Enter**: When prompted for domain name
- **No Parameters**: Run script without SSL flags
- **Continue Anyway**: Proceed despite domain warnings

## 🎯 **Best Practices**

### **Before Running Setup**
1. **Configure DNS**: Point your domain to your server's IP
2. **Check Firewall**: Ensure ports 80/443 are open
3. **Verify Domain**: Test domain resolution with `dig yourdomain.com`
4. **Prepare Email**: Have a valid email for Let's Encrypt notifications

### **During Setup**
1. **Read Prompts**: Pay attention to SSL requirements
2. **Validate Domain**: Check if domain validation passes
3. **Confirm Setup**: Proceed only if domain is properly configured
4. **Monitor Progress**: Watch for SSL setup success messages

### **After Setup**
1. **Test HTTPS**: Visit `https://yourdomain.com`
2. **Check Redirect**: Verify HTTP redirects to HTTPS
3. **Monitor Renewal**: Check certificate renewal status
4. **Update DNS**: Fix any domain configuration issues

## 🔍 **Testing the Interactive SSL Prompt**

You can test the SSL prompt functionality:

```bash
# Test the interactive SSL prompt
./test_ssl_prompt.sh
```

This will show you exactly what the SSL configuration prompts look like without running the full setup.

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Issue: "Could not verify domain configuration"**
- Check internet connectivity
- Verify domain name is correct
- Ensure DNS tools are available

#### **Issue: "Domain validation failed"**
- Update DNS records
- Wait for DNS propagation
- Check domain spelling

#### **Issue: "SSL setup skipped"**
- Provide domain name when prompted
- Provide email address when prompted
- Check domain configuration

### **Manual SSL Setup**
If interactive setup fails, you can set up SSL manually:

```bash
# Use the dedicated SSL setup script
sudo ./setup_ssl.sh -d yourdomain.com -e admin@yourdomain.com
```

## 🎉 **Expected Results**

After successful interactive SSL setup:

```bash
[SUCCESS] SSL certificate obtained and configured successfully!
[SUCCESS] SSL is working correctly!
[SUCCESS] HTTP to HTTPS redirect is working
[SUCCESS] Automatic SSL certificate renewal configured
[SUCCESS] Setup completed successfully!

Access Information:
  - Web Interface: https://yourdomain.com (SSL enabled)
  - HTTP Redirect: http://yourdomain.com (redirects to HTTPS)
  - Admin Login: /admin/login
```

---

**The VPS setup script now includes interactive SSL configuration prompts, making it easy to set up free SSL certificates during the initial installation!** 🔒🚀
