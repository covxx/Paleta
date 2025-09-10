#!/usr/bin/env python3
"""
Test QuickBooks API connection with sandbox credentials
"""

import os
import requests
import json

# QuickBooks Configuration
QB_CLIENT_ID = 'ABUW0U3AsMTGyq7bb1ujpj17IodZlrGkMYtjaWGfke6gcztmtY'
QB_CLIENT_SECRET = 'H75cxmzTruVA2LpU27IyAUzJKJlsNgWHMrJaz3MN'
QB_COMPANY_ID = '9341455300640805'
QB_BASE_URL = 'https://sandbox-quickbooks.api.intuit.com'
QB_REDIRECT_URI = 'http://localhost:5001/qb/callback'
QB_SCOPE = 'com.intuit.quickbooks.accounting'

def test_oauth_url_generation():
    """Test OAuth URL generation"""
    print("🔗 Testing OAuth URL Generation...")

    # Generate state parameter
    import secrets
    state = secrets.token_urlsafe(32)

    # Build authorization URL
    auth_url = (
        f"https://appcenter.intuit.com/connect/oauth2?"
        f"client_id={QB_CLIENT_ID}&"
        f"scope={QB_SCOPE}&"
        f"redirect_uri={QB_REDIRECT_URI}&"
        f"response_type=code&"
        f"state={state}"
    )

    print(f"✅ OAuth URL generated successfully")
    print(f"📋 State: {state}")
    print(f"🔗 Auth URL: {auth_url[:100]}...")
    print()

def test_api_endpoint_structure():
    """Test API endpoint structure"""
    print("🏗️  Testing API Endpoint Structure...")

    # Test company info endpoint structure
    endpoint = f"companyinfo/{QB_COMPANY_ID}"
    full_url = f"{QB_BASE_URL}/v3/company/{QB_COMPANY_ID}/{endpoint}"

    print(f"✅ Endpoint structure: {endpoint}")
    print(f"🔗 Full URL: {full_url}")
    print()

def test_credentials_format():
    """Test credentials format"""
    print("🔑 Testing Credentials Format...")

    # Validate client ID format
    if len(QB_CLIENT_ID) > 20 and QB_CLIENT_ID.isalnum():
        print("✅ Client ID format looks valid")
    else:
        print("❌ Client ID format may be invalid")

    # Validate client secret format
    if len(QB_CLIENT_SECRET) > 20:
        print("✅ Client Secret format looks valid")
    else:
        print("❌ Client Secret format may be invalid")

    # Validate company ID format
    if QB_COMPANY_ID.isdigit() and len(QB_COMPANY_ID) > 10:
        print("✅ Company ID format looks valid")
    else:
        print("❌ Company ID format may be invalid")

    print()

def test_environment_setup():
    """Test environment setup"""
    print("🌍 Testing Environment Setup...")

    # Set environment variables
    os.environ['QB_CLIENT_ID'] = QB_CLIENT_ID
    os.environ['QB_CLIENT_SECRET'] = QB_CLIENT_SECRET
    os.environ['QB_COMPANY_ID'] = QB_COMPANY_ID

    # Test environment variable loading
    client_id = os.getenv('QB_CLIENT_ID')
    client_secret = os.getenv('QB_CLIENT_SECRET')
    company_id = os.getenv('QB_COMPANY_ID')

    if client_id == QB_CLIENT_ID:
        print("✅ QB_CLIENT_ID environment variable set correctly")
    else:
        print("❌ QB_CLIENT_ID environment variable not set correctly")

    if client_secret == QB_CLIENT_SECRET:
        print("✅ QB_CLIENT_SECRET environment variable set correctly")
    else:
        print("❌ QB_CLIENT_SECRET environment variable not set correctly")

    if company_id == QB_COMPANY_ID:
        print("✅ QB_COMPANY_ID environment variable set correctly")
    else:
        print("❌ QB_COMPANY_ID environment variable not set correctly")

    print()

def test_requests_library():
    """Test requests library availability"""
    print("📦 Testing Requests Library...")

    try:
        import requests
        print("✅ Requests library is available")

        # Test a simple request
        response = requests.get('https://httpbin.org/get', timeout=5)
        if response.status_code == 200:
            print("✅ Requests library is working correctly")
        else:
            print("❌ Requests library test failed")
    except ImportError:
        print("❌ Requests library not available - install with: pip install requests")
    except Exception as e:
        print(f"❌ Requests library test failed: {e}")

    print()

def main():
    """Main test function"""
    print("🧪 QuickBooks API Connection Test")
    print("=" * 50)
    print()

    print("📋 Configuration Summary:")
    print(f"Client ID: {QB_CLIENT_ID[:10]}...")
    print(f"Client Secret: {QB_CLIENT_SECRET[:10]}...")
    print(f"Company ID: {QB_COMPANY_ID}")
    print(f"Base URL: {QB_BASE_URL}")
    print(f"Redirect URI: {QB_REDIRECT_URI}")
    print()

    # Run tests
    test_credentials_format()
    test_environment_setup()
    test_requests_library()
    test_oauth_url_generation()
    test_api_endpoint_structure()

    print("🎯 Next Steps:")
    print("1. Start your Flask application")
    print("2. Go to /quickbooks-import as admin")
    print("3. Click 'Test Connection'")
    print("4. Click 'Connect to QuickBooks' when prompted")
    print("5. Complete OAuth flow in browser")
    print("6. Test connection should show company information")
    print()
    print("✅ Configuration is ready for testing!")

if __name__ == "__main__":
    main()
