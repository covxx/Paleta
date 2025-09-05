# QuickBooks Customer Import Debug Fix

Added debugging and improved field mapping to fix customer name import issues.

## 🐛 **Issue Identified**

Customers are importing but the name field is not being populated correctly:
- ✅ **Email and phone** are coming through
- ❌ **Name field** is empty or not showing

## 🔍 **Root Cause Analysis**

The issue could be:
1. **Field Name Mismatch**: QuickBooks API might use different field names
2. **Empty Data**: Sandbox customers might not have names populated
3. **Response Structure**: API response might have different structure than expected

## ✅ **Fixes Implemented**

### **1. Added Debug Logging**
```python
# Debug: Log the actual customer data from QuickBooks
print(f"DEBUG: QB Customer data: {json.dumps(qb_customer, indent=2)}")
```

### **2. Enhanced Field Mapping with Fallbacks**
```python
# Before (❌ Single field mapping)
'name': qb_customer.get('Name', ''),

# After (✅ Multiple fallbacks)
'name': qb_customer.get('Name') or qb_customer.get('DisplayName') or qb_customer.get('CompanyName') or 'Unknown Customer',
```

### **3. Improved Email and Phone Mapping**
```python
# Email with fallbacks
'email': qb_customer.get('PrimaryEmailAddr', {}).get('Address', '') or qb_customer.get('EmailAddr', {}).get('Address', ''),

# Phone with fallbacks
'phone': qb_customer.get('PrimaryPhone', {}).get('FreeFormNumber', '') or qb_customer.get('Phone', {}).get('FreeFormNumber', ''),
```

## 🔧 **Field Mapping Options**

### **Name Field Alternatives**
- `Name` - Primary name field
- `DisplayName` - Display name field
- `CompanyName` - Company name field
- `GivenName` + `FamilyName` - First and last name
- `Unknown Customer` - Fallback if none found

### **Email Field Alternatives**
- `PrimaryEmailAddr.Address` - Primary email
- `EmailAddr.Address` - Alternative email field

### **Phone Field Alternatives**
- `PrimaryPhone.FreeFormNumber` - Primary phone
- `Phone.FreeFormNumber` - Alternative phone field

## 🧪 **Testing the Fix**

### **Step 1: Run Customer Import**
1. **Start the app**: `source venv/bin/activate && python app.py`
2. **Go to QB Import**: Navigate to QuickBooks import page
3. **Click Import Customers**: Start the import process
4. **Check Console**: Look for DEBUG messages in the terminal

### **Step 2: Analyze Debug Output**
Look for messages like:
```
DEBUG: QB Customer data: {
  "Id": "1",
  "Name": "John Doe",
  "DisplayName": "John Doe",
  "PrimaryEmailAddr": {
    "Address": "john@example.com"
  },
  "PrimaryPhone": {
    "FreeFormNumber": "(555) 123-4567"
  }
}
```

### **Step 3: Compare with Expected**
Compare the actual response with expected structure:
- Are the field names correct?
- Is the data populated?
- Are there alternative field names?

## 📋 **Expected QuickBooks Response Structure**

### **Full Customer Response**
```json
{
  "QueryResponse": {
    "Customer": [
      {
        "Id": "1",
        "Name": "John Doe",
        "DisplayName": "John Doe",
        "CompanyName": "Doe Enterprises",
        "PrimaryEmailAddr": {
          "Address": "john.doe@example.com"
        },
        "PrimaryPhone": {
          "FreeFormNumber": "(555) 123-4567"
        },
        "BillAddr": {
          "Name": "John Doe",
          "Line1": "123 Main St",
          "City": "Anytown",
          "CountrySubDivisionCode": "CA",
          "PostalCode": "12345"
        },
        "ShipAddr": {
          "Name": "John Doe",
          "Line1": "123 Main St",
          "City": "Anytown",
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

## 🔍 **Common Issues and Solutions**

### **Issue 1: No Name Field**
**Symptoms**: Name shows as empty or "Unknown Customer"
**Solution**: Check if QuickBooks uses `DisplayName` or `CompanyName` instead

### **Issue 2: Different Field Structure**
**Symptoms**: Email/phone work but name doesn't
**Solution**: Update field mapping based on actual API response

### **Issue 3: Empty Sandbox Data**
**Symptoms**: All fields are empty
**Solution**: Create test customers in QuickBooks sandbox

## 🛠️ **Manual Field Mapping Update**

If the debug output shows different field names, update the mapping:

```python
# Example: If QuickBooks uses 'CompanyName' instead of 'Name'
'name': qb_customer.get('CompanyName') or qb_customer.get('Name') or 'Unknown Customer',

# Example: If QuickBooks uses 'Email' instead of 'PrimaryEmailAddr'
'email': qb_customer.get('Email', {}).get('Address', '') or qb_customer.get('PrimaryEmailAddr', {}).get('Address', ''),
```

## 📊 **Debug Output Analysis**

### **What to Look For**
1. **Field Names**: Are they what we expect?
2. **Data Values**: Are they populated?
3. **Structure**: Is the nesting correct?
4. **Alternatives**: Are there other field names?

### **Example Debug Output**
```
DEBUG: QB Customer data: {
  "Id": "1",
  "DisplayName": "Test Customer",  // ← Name might be here
  "CompanyName": "Test Company",   // ← Or here
  "PrimaryEmailAddr": {
    "Address": "test@example.com"
  },
  "PrimaryPhone": {
    "FreeFormNumber": "(555) 123-4567"
  }
}
```

## 🎯 **Next Steps**

1. **Run the import** and check debug output
2. **Identify the actual field names** used by QuickBooks
3. **Update field mapping** if needed
4. **Test the import** again
5. **Remove debug logging** once fixed

## 🔧 **Quick Fix Commands**

### **Test Customer Import**
```bash
# Start the app
source venv/bin/activate && python app.py

# In browser: Go to QuickBooks import page
# Click "Import Customers"
# Check terminal for DEBUG output
```

### **Remove Debug Logging (After Fix)**
```python
# Remove this line once debugging is complete
print(f"DEBUG: QB Customer data: {json.dumps(qb_customer, indent=2)}")
```

---

**The customer import now has enhanced debugging and improved field mapping with fallbacks. Run the import and check the console output to see the actual QuickBooks response structure.**
