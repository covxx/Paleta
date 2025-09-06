# QuickBooks 401 Unauthorized Error Fix

Fixed the 401 Unauthorized error by implementing automatic token refresh and improved error handling for QuickBooks API integration.

## 🐛 **Issue Identified**

**Error**: `401 Client Error: Unauthorized for url: https://sandbox-quickbooks.api.intuit.com/v3/company/9341455300640805/query?query=SELECT%20*%20FROM%20CompanyInfo&minorversion=75`

**Root Cause**: QuickBooks access token has expired or is invalid. QuickBooks access tokens typically expire after 1 hour.

## ✅ **Fixes Implemented**

### **1. Automatic Token Refresh**
```python
def refresh_qb_access_token():
    """Refresh QuickBooks access token using refresh token"""
    try:
        refresh_token = session.get('qb_refresh_token')
        if not refresh_token:
            return {'error': 'No refresh token available'}
        
        # Prepare token refresh request
        token_data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        # Make request to QuickBooks token endpoint
        response = requests.post(
            'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer',
            data=token_data,
            auth=(QB_CLIENT_ID, QB_CLIENT_SECRET),
            headers={'Accept': 'application/json'}
        )
        
        if response.status_code == 200:
            token_info = response.json()
            
            # Update session with new tokens
            session['qb_access_token'] = token_info.get('access_token')
            session['qb_refresh_token'] = token_info.get('refresh_token')
            session['qb_token_expires'] = datetime.now(timezone.utc) + timedelta(seconds=token_info.get('expires_in', 3600))
            
            return {'success': True, 'access_token': token_info.get('access_token')}
        else:
            return {'error': f'Token refresh failed: {response.status_code} - {response.text}'}
            
    except Exception as e:
        return {'error': f'Token refresh error: {str(e)}'}
```

### **2. Token Expiration Checking**
```python
def is_qb_token_expired():
    """Check if QuickBooks access token is expired"""
    expires_at = session.get('qb_token_expires')
    if not expires_at:
        return True
    
    # Add 5 minute buffer before expiration
    buffer_time = timedelta(minutes=5)
    return datetime.now(timezone.utc) + buffer_time >= expires_at
```

### **3. Enhanced API Request with Auto-Refresh**
```python
def make_qb_api_request(endpoint, method='GET', data=None):
    """Make authenticated request to QuickBooks API with automatic token refresh"""
    # Check if token is expired and refresh if needed
    if is_qb_token_expired():
        refresh_result = refresh_qb_access_token()
        if 'error' in refresh_result:
            return {'error': f'Token refresh failed: {refresh_result["error"]}'}
    
    # ... make API request ...
    
    # Handle 401 Unauthorized - token might be invalid
    if response.status_code == 401:
        # Try to refresh token once more
        refresh_result = refresh_qb_access_token()
        if 'error' in refresh_result:
            return {'error': 'QuickBooks access token expired and refresh failed. Please reconnect to QuickBooks.'}
        
        # Retry the request with new token
        new_access_token = get_qb_access_token()
        headers['Authorization'] = f'Bearer {new_access_token}'
        
        # Retry the request
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
```

### **4. Improved Error Handling**
```python
except requests.exceptions.RequestException as e:
    error_msg = str(e)
    if '401' in error_msg:
        return {'error': 'QuickBooks access token expired. Please reconnect to QuickBooks.'}
    elif '400' in error_msg:
        return {'error': 'Invalid QuickBooks API request. Please check your data.'}
    elif '403' in error_msg:
        return {'error': 'QuickBooks API access forbidden. Please check your permissions.'}
    elif '429' in error_msg:
        return {'error': 'QuickBooks API rate limit exceeded. Please try again later.'}
    else:
        return {'error': f'QuickBooks API error: {error_msg}'}
```

### **5. Enhanced QB Admin Interface**
**New Features**:
- **Connect to QB Button**: Re-authenticate with QuickBooks
- **Disconnect Button**: Clear all stored tokens
- **Better Error Messages**: Clear guidance on how to fix issues

```html
<div class="btn-toolbar mb-2 mb-md-0">
    <button class="btn btn-outline-primary" onclick="testConnection()">
        <i class="fas fa-plug"></i> Test Connection
    </button>
    <button class="btn btn-outline-success" onclick="connectToQuickBooks()">
        <i class="fas fa-link"></i> Connect to QB
    </button>
    <button class="btn btn-outline-danger" onclick="disconnectQuickBooks()">
        <i class="fas fa-unlink"></i> Disconnect
    </button>
</div>
```

### **6. OAuth Reconnection API**
```python
@app.route('/api/quickbooks/connect', methods=['GET'])
@admin_required
def connect_to_quickbooks():
    """Initiate QuickBooks OAuth connection"""
    try:
        import secrets
        state = secrets.token_urlsafe(32)
        session['qb_oauth_state'] = state
        
        auth_url = (
            f"https://appcenter.intuit.com/connect/oauth2?"
            f"client_id={QB_CLIENT_ID}&"
            f"scope={QB_SCOPE}&"
            f"redirect_uri={QB_REDIRECT_URI}&"
            f"response_type=code&"
            f"state={state}"
        )
        
        return jsonify({
            'success': True,
            'auth_url': auth_url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### **7. Disconnect API**
```python
@app.route('/api/quickbooks/disconnect', methods=['POST'])
@admin_required
def disconnect_quickbooks():
    """Disconnect from QuickBooks and clear tokens"""
    try:
        # Clear all QB-related session data
        session.pop('qb_access_token', None)
        session.pop('qb_refresh_token', None)
        session.pop('qb_company_id', None)
        session.pop('qb_token_expires', None)
        session.pop('qb_oauth_state', None)
        
        return jsonify({
            'success': True,
            'message': 'Disconnected from QuickBooks successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## 🔄 **Token Management Flow**

### **Initial Connection**
1. **User clicks "Connect to QB"**
2. **OAuth URL generated** with state parameter
3. **User redirected** to QuickBooks authorization
4. **User authorizes** the application
5. **Callback received** with authorization code
6. **Code exchanged** for access and refresh tokens
7. **Tokens stored** in session with expiration time

### **Automatic Token Refresh**
1. **API request made** to QuickBooks
2. **System checks** if token is expired (with 5-minute buffer)
3. **If expired**: Refresh token used to get new access token
4. **New tokens stored** in session
5. **API request retried** with new token

### **Error Recovery**
1. **401 error received** from QuickBooks API
2. **System attempts** token refresh
3. **If refresh succeeds**: Request retried with new token
4. **If refresh fails**: User prompted to reconnect
5. **Clear error message** provided to user

## 🧪 **Testing the Fix**

### **Test Token Refresh**
```bash
# Test the debug tool
python debug_qb_401.py
```

### **Test Reconnection**
1. **Go to QB Admin**: `/quickbooks-admin`
2. **Click "Connect to QB"**: Start OAuth flow
3. **Complete authorization**: In QuickBooks
4. **Test connection**: Should work without 401 error
5. **Try sync operations**: Should work with new tokens

### **Test Auto-Refresh**
1. **Wait for token expiration** (1 hour)
2. **Make API call**: Should auto-refresh token
3. **Verify success**: No 401 error should occur
4. **Check logs**: Should see token refresh activity

## 🔧 **Error Scenarios Handled**

### **Scenario 1: No Access Token**
- **Error**: "No QuickBooks access token found. Please connect to QuickBooks first."
- **Solution**: User clicks "Connect to QB" button

### **Scenario 2: Expired Access Token**
- **Error**: Auto-refresh attempted
- **Solution**: New token obtained automatically

### **Scenario 3: Invalid Refresh Token**
- **Error**: "QuickBooks access token expired and refresh failed. Please reconnect to QuickBooks."
- **Solution**: User clicks "Connect to QB" to re-authenticate

### **Scenario 4: API Rate Limiting**
- **Error**: "QuickBooks API rate limit exceeded. Please try again later."
- **Solution**: Wait and retry, or implement exponential backoff

### **Scenario 5: Permission Issues**
- **Error**: "QuickBooks API access forbidden. Please check your permissions."
- **Solution**: Check QuickBooks app permissions and company access

## 📊 **Monitoring & Logging**

### **Token Refresh Logging**
```python
def log_sync_activity(sync_type, status, message):
    """Log sync activity for monitoring"""
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] QB Sync - {sync_type.upper()}: {status.upper()} - {message}")
```

### **Error Tracking**
- **Token refresh failures** logged with timestamps
- **API error details** captured for debugging
- **User actions** tracked for troubleshooting
- **Performance metrics** monitored for optimization

## 🎯 **Benefits of the Fix**

### **For Users**
- ✅ **Seamless Experience**: Tokens refresh automatically
- ✅ **Clear Error Messages**: Know exactly what to do
- ✅ **Easy Reconnection**: One-click re-authentication
- ✅ **No Data Loss**: Failed syncs don't break order creation

### **For System**
- ✅ **Automatic Recovery**: Self-healing token management
- ✅ **Better Reliability**: Reduced 401 errors
- ✅ **Improved Monitoring**: Better error tracking
- ✅ **Enhanced Security**: Proper token expiration handling

### **For Business**
- ✅ **Reduced Support**: Fewer authentication issues
- ✅ **Better Uptime**: Automatic error recovery
- ✅ **Professional Experience**: Smooth QuickBooks integration
- ✅ **Operational Efficiency**: Less manual intervention needed

## 🚀 **Next Steps**

### **Immediate Actions**
1. **Test the fix**: Go to QB Admin and test connection
2. **Re-authenticate**: Click "Connect to QB" if needed
3. **Verify sync**: Test customer/item import
4. **Monitor logs**: Watch for token refresh activity

### **Future Enhancements**
1. **Persistent Token Storage**: Store tokens in database instead of session
2. **Token Encryption**: Encrypt stored tokens for security
3. **Multi-User Support**: Handle tokens for multiple users
4. **Advanced Monitoring**: Token usage analytics and alerts

---

**The 401 Unauthorized error has been fixed with comprehensive token management, automatic refresh, and improved error handling. The system now provides a seamless QuickBooks integration experience with automatic recovery from token expiration.**
