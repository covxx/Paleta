# QuickBooks Query Endpoint Fix

Fixed the 400 error by correcting the QuickBooks API query endpoint usage from POST with body to GET with URL parameters.

## 🐛 **Issue Identified**

The 400 error was occurring because:
1. **Wrong HTTP Method**: Using POST instead of GET for query requests
2. **Wrong Parameter Format**: Sending query in request body instead of URL parameters
3. **Missing minorversion**: QuickBooks API requires minorversion parameter
4. **Incorrect URL Structure**: Not following QuickBooks API specification

## ✅ **Fixes Implemented**

### **1. Fixed Items Import**
**Before:**
```python
query_data = {
    "query": "SELECT * FROM Item WHERE Type = 'Inventory'"
}
result = make_qb_api_request('query', method='POST', data=query_data)  # ❌ Wrong
```

**After:**
```python
query = "SELECT * FROM Item WHERE Type = 'Inventory'"
result = make_qb_api_request(f'query?query={query}&minorversion=75')  # ✅ Correct
```

### **2. Fixed Customers Import**
**Before:**
```python
query_data = {
    "query": "SELECT * FROM Customer"
}
result = make_qb_api_request('query', method='POST', data=query_data)  # ❌ Wrong
```

**After:**
```python
query = "SELECT * FROM Customer"
result = make_qb_api_request(f'query?query={query}&minorversion=75')  # ✅ Correct
```

### **3. Fixed Company Info Test**
**Before:**
```python
result = make_qb_api_request('companyinfo/1')  # ❌ Wrong endpoint
```

**After:**
```python
query = "SELECT * FROM CompanyInfo"
result = make_qb_api_request(f'query?query={query}&minorversion=75')  # ✅ Correct
```

## 🔧 **Correct QuickBooks API Structure**

### **Query Endpoint Format**
```
GET /v3/company/{companyId}/query?query=<selectStatement>&minorversion=75
```

### **Example URLs**
- **Company Info**: `GET /v3/company/9341455300640805/query?query=SELECT%20*%20FROM%20CompanyInfo&minorversion=75`
- **Items**: `GET /v3/company/9341455300640805/query?query=SELECT%20*%20FROM%20Item%20WHERE%20Type%20%3D%20%27Inventory%27&minorversion=75`
- **Customers**: `GET /v3/company/9341455300640805/query?query=SELECT%20*%20FROM%20Customer&minorversion=75`

### **Key Parameters**
- **query**: SQL-like select statement (URL encoded)
- **minorversion**: API version (75 is current)
- **Method**: GET (not POST)
- **Headers**: Authorization Bearer token required

## 📋 **API Call Examples**

### **Items Query**
```bash
GET https://sandbox-quickbooks.api.intuit.com/v3/company/9341455300640805/query?query=SELECT%20*%20FROM%20Item%20WHERE%20Type%20%3D%20%27Inventory%27&minorversion=75
Authorization: Bearer {access_token}
Accept: application/json
```

### **Customers Query**
```bash
GET https://sandbox-quickbooks.api.intuit.com/v3/company/9341455300640805/query?query=SELECT%20*%20FROM%20Customer&minorversion=75
Authorization: Bearer {access_token}
Accept: application/json
```

### **Company Info Query**
```bash
GET https://sandbox-quickbooks.api.intuit.com/v3/company/9341455300640805/query?query=SELECT%20*%20FROM%20CompanyInfo&minorversion=75
Authorization: Bearer {access_token}
Accept: application/json
```

## 📄 **Expected Response Format**

### **Company Info Response**
```json
{
  "QueryResponse": {
    "CompanyInfo": [
      {
        "Id": "9341455300640805",
        "CompanyName": "Test Company",
        "LegalName": "Test Company LLC",
        "CompanyAddr": {
          "Line1": "123 Test St",
          "City": "Test City",
          "CountrySubDivisionCode": "CA",
          "PostalCode": "12345"
        }
      }
    ],
    "maxResults": 1,
    "startPosition": 1
  }
}
```

### **Items Response**
```json
{
  "QueryResponse": {
    "Item": [
      {
        "Id": "1",
        "Name": "Test Item",
        "Type": "Inventory",
        "Sku": "SKU001",
        "Description": "Test description"
      }
    ],
    "maxResults": 1,
    "startPosition": 1
  }
}
```

## 🚀 **How It Works Now**

### **Items Import Process**
1. **Query Request**: GET to `/v3/company/{companyId}/query?query=SELECT%20*%20FROM%20Item%20WHERE%20Type%20%3D%20%27Inventory%27&minorversion=75`
2. **Response**: QuickBooks returns items in QueryResponse format
3. **Processing**: Items are imported and stored in local database

### **Customers Import Process**
1. **Query Request**: GET to `/v3/company/{companyId}/query?query=SELECT%20*%20FROM%20Customer&minorversion=75`
2. **Response**: QuickBooks returns customers in QueryResponse format
3. **Processing**: Customers are imported and stored in local database

### **Company Info Test**
1. **Query Request**: GET to `/v3/company/{companyId}/query?query=SELECT%20*%20FROM%20CompanyInfo&minorversion=75`
2. **Response**: QuickBooks returns company info in QueryResponse format
3. **Display**: Company name and details are shown in the UI

## 🧪 **Testing the Fix**

### **Test Items Import**
1. **Connect to QuickBooks**: Complete OAuth flow
2. **Go to QB Import Page**: Navigate to QuickBooks import
3. **Click Import Items**: Should now work without 400 error
4. **Check Results**: Items should be imported successfully

### **Test Customers Import**
1. **Click Import Customers**: Should work without 400 error
2. **Check Results**: Customers should be imported successfully

### **Test Company Info**
1. **Click Test Connection**: Should show company name instead of "Unknown"
2. **Check Response**: Company details should be displayed

## 🔍 **Troubleshooting**

### **If Still Getting 400 Errors**
1. **Check Access Token**: Ensure OAuth flow completed successfully
2. **Verify Company ID**: Confirm sandbox company ID is correct
3. **Check Query Syntax**: Ensure SQL-like query syntax is correct
4. **Review URL Encoding**: Verify query parameters are properly encoded

### **Common Issues**
- **Invalid Query Syntax**: Use proper SQL-like syntax for QuickBooks
- **Missing minorversion**: Always include `&minorversion=75`
- **Wrong HTTP Method**: Use GET, not POST for queries
- **URL Encoding**: Ensure special characters are properly encoded

### **Debug Commands**
```bash
# Test the fixed endpoints
curl -X GET "http://localhost:5001/api/quickbooks/test-connection" \
  -H "Authorization: Bearer {access_token}"

curl -X POST http://localhost:5001/api/quickbooks/import/items \
  -H "Content-Type: application/json"

curl -X POST http://localhost:5001/api/quickbooks/import/customers \
  -H "Content-Type: application/json"
```

## 📚 **QuickBooks API Best Practices**

### **Query Optimization**
- Use specific WHERE clauses to limit results
- Request only needed fields when possible
- Use pagination for large datasets
- Always include minorversion parameter

### **Error Handling**
- Check for QueryResponse in API responses
- Handle empty result sets gracefully
- Implement proper retry logic for rate limits
- Validate response structure before processing

### **Data Processing**
- Validate data before importing
- Handle missing or null fields
- Map QuickBooks fields to local database schema
- Process QueryResponse format correctly

---

**The QuickBooks API query endpoint issue has been resolved. All imports (items, customers) and company info should now work correctly using the proper GET request format with URL parameters.**
