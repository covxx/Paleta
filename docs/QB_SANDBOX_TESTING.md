# QuickBooks Sandbox Testing Setup

The QuickBooks integration is now configured with sandbox credentials for testing.

## 🔧 **Sandbox Configuration**

### **Credentials**
- **Client ID**: `ABUW0U3AsMTGyq7bb1ujpj17IodZlrGkMYtjaWGfke6gcztmtY`
- **Client Secret**: `H75cxmzTruVA2LpU27IyAUzJKJlsNgWHMrJaz3MN`
- **Company ID**: `9341455300640805` (Sandbox Company)
- **Base URL**: `https://sandbox-quickbooks.api.intuit.com`

### **Environment**
- **Sandbox Mode**: ✅ Enabled
- **OAuth URL**: `https://appcenter.intuit.com/connect/oauth2`
- **Redirect URI**: `http://localhost:5001/qb/callback`
- **Scope**: `com.intuit.quickbooks.accounting`

## 🧪 **Testing Status**

### **Configuration Tests**
- ✅ Client ID format valid
- ✅ Client Secret format valid  
- ✅ Company ID format valid
- ✅ Environment variables set correctly
- ✅ Requests library available and working
- ✅ OAuth URL generation working
- ✅ API endpoint structure correct

### **Ready for Testing**
All configuration tests passed successfully. The system is ready for QuickBooks sandbox testing.

## 🚀 **How to Test**

### **Step 1: Start the Application**
```bash
# Activate virtual environment
source venv/bin/activate

# Start Flask application
python app.py
```

### **Step 2: Access QuickBooks Import**
1. Open browser to `http://localhost:5001`
2. Log in as admin
3. Navigate to QuickBooks Import page

### **Step 3: Test Connection**
1. Click "Test Connection" button
2. You should see: "Please connect to QuickBooks first using the OAuth flow"
3. Click "Connect to QuickBooks" button

### **Step 4: OAuth Flow**
1. You'll be redirected to QuickBooks authorization page
2. Log in with your QuickBooks sandbox account
3. Authorize the application
4. You'll be redirected back to the application

### **Step 5: Verify Connection**
1. The page should show "Connected to QuickBooks"
2. Company information should be displayed
3. You can now test importing customers and items

## 📋 **API Endpoints for Testing**

### **Test Connection**
```bash
curl -X GET http://localhost:5001/api/quickbooks/test-connection
```

### **Get OAuth URL**
```bash
curl -X GET http://localhost:5001/api/quickbooks/connect
```

### **OAuth Callback**
```
http://localhost:5001/qb/callback?code=...&state=...&realmId=9341455300640805
```

## 🔍 **Expected Behavior**

### **Before OAuth (No Token)**
```json
{
  "success": false,
  "error": "No access token found",
  "message": "Please connect to QuickBooks first using the OAuth flow",
  "action_required": "oauth_connect"
}
```

### **After OAuth (With Token)**
```json
{
  "success": true,
  "message": "QuickBooks connection successful",
  "company_info": {
    "CompanyName": "Sandbox Company",
    "CompanyAddr": {...},
    "CompanyInfo": {...}
  }
}
```

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **400 Error Still Appearing**
- Ensure you're using the virtual environment: `source venv/bin/activate`
- Check that the Flask app is running on port 5001
- Verify admin login is working

#### **OAuth Redirect Issues**
- Ensure redirect URI matches: `http://localhost:5001/qb/callback`
- Check that the callback route is accessible
- Verify QuickBooks app is configured for sandbox

#### **Token Issues**
- Clear browser session and try again
- Check browser console for JavaScript errors
- Verify OAuth flow completes successfully

### **Debug Commands**
```bash
# Test configuration
source venv/bin/activate && python test_qb_connection.py

# Test Flask app
source venv/bin/activate && python -c "from app import QB_CLIENT_ID, QB_COMPANY_ID; print(f'Client ID: {QB_CLIENT_ID[:10]}...'); print(f'Company ID: {QB_COMPANY_ID}')"

# Test API endpoint
curl -X GET http://localhost:5001/api/quickbooks/test-connection
```

## 📊 **Sandbox Data**

### **Available for Testing**
- **Customers**: Import from sandbox QuickBooks
- **Items**: Import products and services
- **Orders**: Sync orders to QuickBooks
- **Company Info**: Access company details

### **Sandbox Limitations**
- Data is reset periodically
- No real financial transactions
- Limited to test scenarios
- Rate limits may apply

## 🎯 **Next Steps After Testing**

### **Successful Connection**
1. **Import Customers**: Test customer import functionality
2. **Import Items**: Test item/product import
3. **Create Orders**: Test order creation and sync
4. **Verify Data**: Check that data appears correctly

### **Production Preparation**
1. **Get Production Credentials**: Obtain production Client ID and Secret
2. **Update Configuration**: Replace sandbox credentials
3. **Update Company ID**: Use production company ID
4. **Test Production**: Verify with real QuickBooks account

## 🔒 **Security Notes**

### **Sandbox Security**
- Sandbox credentials are safe to use for testing
- No real financial data is involved
- Tokens are stored in session (temporary)

### **Production Security**
- Store credentials securely (environment variables)
- Use HTTPS in production
- Implement proper token storage
- Add token refresh logic

---

**The QuickBooks sandbox integration is fully configured and ready for testing. All configuration tests have passed, and the OAuth flow is properly implemented. You can now test the complete QuickBooks integration workflow.**
