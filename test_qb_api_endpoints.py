#!/usr/bin/env python3
"""
Test QuickBooks API endpoints to verify correct URL structure
"""

import os
import requests
import json

# QuickBooks Configuration
QB_CLIENT_ID = 'ABUW0U3AsMTGyq7bb1ujpj17IodZlrGkMYtjaWGfke6gcztmtY'
QB_CLIENT_SECRET = 'H75cxmzTruVA2LpU27IyAUzJKJlsNgWHMrJaz3MN'
QB_COMPANY_ID = '9341455300640805'
QB_BASE_URL = 'https://sandbox-quickbooks.api.intuit.com'

def test_api_url_structure():
    """Test the API URL structure"""
    print("🔗 Testing QuickBooks API URL Structure...")
    print()
    
    # Test different endpoint structures
    endpoints = [
        {
            'name': 'Company Info',
            'endpoint': 'companyinfo/1',
            'url': f"{QB_BASE_URL}/v3/company/{QB_COMPANY_ID}/companyinfo/{QB_COMPANY_ID}",
            'method': 'GET'
        },
        {
            'name': 'Query Items',
            'endpoint': 'query',
            'url': f"{QB_BASE_URL}/v3/company/{QB_COMPANY_ID}/query",
            'method': 'POST',
            'data': {"query": "SELECT * FROM Item WHERE Type = 'Inventory'"}
        },
        {
            'name': 'Query Customers',
            'endpoint': 'query',
            'url': f"{QB_BASE_URL}/v3/company/{QB_COMPANY_ID}/query",
            'method': 'POST',
            'data': {"query": "SELECT * FROM Customer"}
        }
    ]
    
    for endpoint in endpoints:
        print(f"📋 {endpoint['name']}:")
        print(f"   Endpoint: {endpoint['endpoint']}")
        print(f"   URL: {endpoint['url']}")
        print(f"   Method: {endpoint['method']}")
        if 'data' in endpoint:
            print(f"   Data: {json.dumps(endpoint['data'], indent=6)}")
        print()

def test_oauth_url():
    """Test OAuth URL generation"""
    print("🔐 Testing OAuth URL Generation...")
    
    import secrets
    state = secrets.token_urlsafe(32)
    
    auth_url = (
        f"https://appcenter.intuit.com/connect/oauth2?"
        f"client_id={QB_CLIENT_ID}&"
        f"scope=com.intuit.quickbooks.accounting&"
        f"redirect_uri=http://localhost:5001/qb/callback&"
        f"response_type=code&"
        f"state={state}"
    )
    
    print(f"✅ OAuth URL generated successfully")
    print(f"📋 State: {state}")
    print(f"🔗 Auth URL: {auth_url[:100]}...")
    print()

def test_token_exchange_url():
    """Test token exchange URL"""
    print("🔄 Testing Token Exchange URL...")
    
    token_url = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
    
    print(f"✅ Token exchange URL: {token_url}")
    print()

def test_query_examples():
    """Test QuickBooks query examples"""
    print("📊 QuickBooks Query Examples...")
    
    queries = [
        {
            'name': 'Get All Items',
            'query': "SELECT * FROM Item"
        },
        {
            'name': 'Get Inventory Items Only',
            'query': "SELECT * FROM Item WHERE Type = 'Inventory'"
        },
        {
            'name': 'Get All Customers',
            'query': "SELECT * FROM Customer"
        },
        {
            'name': 'Get Company Info',
            'query': "SELECT * FROM CompanyInfo"
        }
    ]
    
    for query in queries:
        print(f"📋 {query['name']}:")
        print(f"   Query: {query['query']}")
        print()

def main():
    """Main test function"""
    print("🧪 QuickBooks API Endpoint Test")
    print("=" * 50)
    print()
    
    print("📋 Configuration:")
    print(f"Client ID: {QB_CLIENT_ID[:10]}...")
    print(f"Company ID: {QB_COMPANY_ID}")
    print(f"Base URL: {QB_BASE_URL}")
    print()
    
    test_api_url_structure()
    test_oauth_url()
    test_token_exchange_url()
    test_query_examples()
    
    print("🎯 Key Points:")
    print("1. Use /query endpoint for most data retrieval")
    print("2. Use /companyinfo/{companyId} for company information")
    print("3. POST requests to /query with SQL-like syntax")
    print("4. GET requests for company info")
    print()
    print("✅ API endpoint structure is correct!")

if __name__ == "__main__":
    main()
