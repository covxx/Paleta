# QuickBooks API Credentials Update

The QuickBooks API credentials have been updated in the application configuration.

## 🔑 **New Credentials**

### **Client ID**
```
ABUW0U3AsMTGyq7bb1ujpj17IodZlrGkMYtjaWGfke6gcztmtY
```

### **Client Secret**
```
H75cxmzTruVA2LpU27IyAUzJKJlsNgWHMrJaz3MN
```

## 📁 **Files Updated**

### **1. app.py**
Updated the QuickBooks configuration section:
```python
# QuickBooks Online Configuration
QB_CLIENT_ID = os.getenv('QB_CLIENT_ID', 'ABUW0U3AsMTGyq7bb1ujpj17IodZlrGkMYtjaWGfke6gcztmtY')
QB_CLIENT_SECRET = os.getenv('QB_CLIENT_SECRET', 'H75cxmzTruVA2LpU27IyAUzJKJlsNgWHMrJaz3MN')
```

### **2. QUICKBOOKS_SETUP.md**
Updated the documentation with the new credentials for reference.

## 🔧 **Configuration Details**

### **Environment Variable Support**
The application still supports environment variables for flexibility:
- If `QB_CLIENT_ID` environment variable is set, it will use that value
- If not set, it will use the default value (your new credentials)
- Same applies to `QB_CLIENT_SECRET`

### **Current Configuration**
- **Client ID**: `ABUW0U3AsMTGyq7bb1ujpj17IodZlrGkMYtjaWGfke6gcztmtY`
- **Client Secret**: `H75cxmzTruVA2LpU27IyAUzJKJlsNgWHMrJaz3MN`
- **Redirect URI**: `http://localhost:5001/qb/callback` (configurable)
- **Scope**: `com.intuit.quickbooks.accounting`
- **Base URL**: `https://sandbox-quickbooks.api.intuit.com` (sandbox for testing)

## 🚀 **Usage**

### **For Development**
The credentials are now hardcoded as defaults, so the application will work immediately without additional configuration.

### **For Production**
You can still override the credentials using environment variables:
```bash
export QB_CLIENT_ID="your_production_client_id"
export QB_CLIENT_SECRET="your_production_client_secret"
```

### **Environment File (.env)**
Create a `.env` file in your project root:
```bash
# QuickBooks App Credentials
QB_CLIENT_ID=ABUW0U3AsMTGyq7bb1ujpj17IodZlrGkMYtjaWGfke6gcztmtY
QB_CLIENT_SECRET=H75cxmzTruVA2LpU27IyAUzJKJlsNgWHMrJaz3MN

# QuickBooks Company ID (found in your QB company settings)
QB_COMPANY_ID=your_quickbooks_company_id_here

# QuickBooks Redirect URI
QB_REDIRECT_URI=http://localhost:5001/qb/callback
```

## 🔒 **Security Notes**

### **Credential Protection**
- Credentials are now embedded as defaults in the application
- Environment variables can still override for different environments
- `.env` file should be added to `.gitignore` to prevent accidental commits

### **Production Considerations**
- Consider using environment variables in production
- Ensure proper access controls on the QuickBooks app
- Monitor API usage and rate limits

## 🧪 **Testing**

### **Verify Configuration**
```python
# Test the credentials are loaded correctly
import os
print('QB_CLIENT_ID:', os.getenv('QB_CLIENT_ID', 'ABUW0U3AsMTGyq7bb1ujpj17IodZlrGkMYtjaWGfke6gcztmtY'))
print('QB_CLIENT_SECRET:', os.getenv('QB_CLIENT_SECRET', 'H75cxmzTruVA2LpU27IyAUzJKJlsNgWHMrJaz3MN'))
```

### **QuickBooks Connection Test**
1. Log in as admin
2. Navigate to QuickBooks Import page
3. Click "Test Connection" to verify credentials work
4. Check for any error messages

## 📋 **Next Steps**

### **Required Setup**
1. **Company ID**: You'll need to provide your QuickBooks Company ID
2. **Redirect URI**: Update the redirect URI to match your deployment URL
3. **OAuth Flow**: Test the complete OAuth authentication flow

### **QuickBooks App Configuration**
Ensure your QuickBooks app is configured with:
- **Redirect URI**: `http://localhost:5001/qb/callback` (for development)
- **Scopes**: `com.intuit.quickbooks.accounting`
- **Environment**: Sandbox (for testing)

## 🔍 **Troubleshooting**

### **Common Issues**
1. **Invalid Credentials**: Verify the Client ID and Secret are correct
2. **Redirect URI Mismatch**: Ensure the redirect URI matches your app configuration
3. **Company ID Missing**: You'll need to provide the Company ID after OAuth

### **Debug Commands**
```bash
# Check if credentials are loaded
python3 -c "from app import QB_CLIENT_ID, QB_CLIENT_SECRET; print(f'Client ID: {QB_CLIENT_ID[:10]}...'); print(f'Secret: {QB_CLIENT_SECRET[:10]}...')"

# Test QuickBooks connection
curl -X GET http://localhost:5001/api/quickbooks/test-connection
```

---

**The QuickBooks API credentials have been successfully updated and are ready for use. The application will now use these credentials for all QuickBooks API interactions.**
