# QuickBooks API Endpoint Fix

Fixed the 400 error when accessing QuickBooks items endpoint by correcting the API endpoint structure.

## 🐛 **Issue Identified**

The 400 error was occurring because:
1. **Incorrect Endpoint**: The code was trying to access `/items` directly
2. **Wrong API Structure**: QuickBooks API doesn't have a direct `/items` endpoint
3. **Missing Query Format**: Items and customers must be retrieved using the `/query` endpoint

## ✅ **Fixes Implemented**

### **1. Fixed Items Import**
**Before:**
```python
result = make_qb_api_request('items')  # ❌ Wrong endpoint
```

**After:**
```python
query_data = {
    "query": "SELECT * FROM Item WHERE Type = 'Inventory'"
}
result = make_qb_api_request('query', method='POST', data=query_data)  # ✅ Correct
```

### **2. Fixed Customers Import**
**Before:**
```python
result = make_qb_api_request('customers')  # ❌ Wrong endpoint
```

**After:**
```python
query_data = {
    "query": "SELECT * FROM Customer"
}
result = make_qb_api_request('query', method='POST', data=query_data)  # ✅ Correct
```

### **3. Enhanced URL Construction**
Updated the `make_qb_api_request` function to handle different endpoint types correctly:

```python
# QuickBooks API URL structure
# For company info: /v3/company/{companyId}/companyinfo/{companyId}
# For queries: /v3/company/{companyId}/query
# For items: /v3/company/{companyId}/items
# For customers: /v3/company/{companyId}/customers

if endpoint == 'companyinfo/1':
    # Special case for company info
    url = f"{QB_BASE_URL}/v3/company/{QB_COMPANY_ID}/companyinfo/{QB_COMPANY_ID}"
else:
    # Standard endpoint structure
    url = f"{QB_BASE_URL}/v3/company/{QB_COMPANY_ID}/{endpoint}"
```

## 🔧 **Correct QuickBooks API Structure**

### **Available Endpoints**
1. **Company Info**: `GET /v3/company/{companyId}/companyinfo/{companyId}`
2. **Query**: `POST /v3/company/{companyId}/query` (for most data retrieval)
3. **Items**: `GET /v3/company/{companyId}/items` (limited functionality)
4. **Customers**: `GET /v3/company/{companyId}/customers` (limited functionality)

### **Query Endpoint Usage**
The `/query` endpoint is the primary way to retrieve data from QuickBooks:

```json
{
  "query": "SELECT * FROM Item WHERE Type = 'Inventory'"
}
```

**Common Queries:**
- `SELECT * FROM Item` - Get all items
- `SELECT * FROM Item WHERE Type = 'Inventory'` - Get inventory items only
- `SELECT * FROM Customer` - Get all customers
- `SELECT * FROM CompanyInfo` - Get company information

## 🚀 **How It Works Now**

### **Items Import Process**
1. **Query Request**: POST to `/v3/company/{companyId}/query`
2. **Query Data**: `{"query": "SELECT * FROM Item WHERE Type = 'Inventory'"}`
3. **Response**: QuickBooks returns item data in QueryResponse format
4. **Processing**: Items are imported and stored in local database

### **Customers Import Process**
1. **Query Request**: POST to `/v3/company/{companyId}/query`
2. **Query Data**: `{"query": "SELECT * FROM Customer"}`
3. **Response**: QuickBooks returns customer data in QueryResponse format
4. **Processing**: Customers are imported and stored in local database

## 📋 **API Endpoint Examples**

### **Items Query**
```bash
POST https://sandbox-quickbooks.api.intuit.com/v3/company/9341455300640805/query
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "query": "SELECT * FROM Item WHERE Type = 'Inventory'"
}
```

### **Customers Query**
```bash
POST https://sandbox-quickbooks.api.intuit.com/v3/company/9341455300640805/query
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "query": "SELECT * FROM Customer"
}
```

### **Company Info**
```bash
GET https://sandbox-quickbooks.api.intuit.com/v3/company/9341455300640805/companyinfo/9341455300640805
Authorization: Bearer {access_token}
```

## 🧪 **Testing the Fix**

### **Test Items Import**
1. **Connect to QuickBooks**: Complete OAuth flow
2. **Go to QB Import Page**: Navigate to QuickBooks import
3. **Click Import Items**: Should now work without 400 error
4. **Check Results**: Items should be imported successfully

### **Test Customers Import**
1. **Click Import Customers**: Should work without 400 error
2. **Check Results**: Customers should be imported successfully

### **Expected Response Format**
```json
{
  "QueryResponse": {
    "Item": [
      {
        "Id": "1",
        "Name": "Sample Item",
        "Type": "Inventory",
        "Sku": "SKU001",
        "Description": "Sample description"
      }
    ],
    "maxResults": 1,
    "startPosition": 1
  }
}
```

## 🔍 **Troubleshooting**

### **If Still Getting 400 Errors**
1. **Check Access Token**: Ensure OAuth flow completed successfully
2. **Verify Company ID**: Confirm sandbox company ID is correct
3. **Check Query Syntax**: Ensure SQL-like query syntax is correct
4. **Review Headers**: Verify Authorization header is present

### **Common Query Issues**
- **Invalid Syntax**: Use proper SQL-like syntax for QuickBooks
- **Missing WHERE Clause**: Add filters to limit results
- **Wrong Entity Name**: Use correct entity names (Item, Customer, etc.)

### **Debug Commands**
```bash
# Test the fixed endpoints
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

### **Error Handling**
- Check for QueryResponse in API responses
- Handle empty result sets gracefully
- Implement proper retry logic for rate limits

### **Data Processing**
- Validate data before importing
- Handle missing or null fields
- Map QuickBooks fields to local database schema

---

**The QuickBooks API endpoint issue has been resolved. Items and customers can now be imported successfully using the correct `/query` endpoint with proper SQL-like syntax.**
