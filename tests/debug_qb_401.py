#!/usr/bin/env python3
"""
Debug QuickBooks 401 Unauthorized Error
"""

import os
import sys
import requests
import json
from datetime import datetime, timezone, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_qb_token_refresh():
    """Test QuickBooks token refresh functionality"""
    print("🔍 Testing QuickBooks Token Refresh")
    print("=" * 40)
    print()

    # QuickBooks Configuration
    QB_CLIENT_ID = 'ABUW0U3AsMTGyq7bb1ujpj17IodZlrGkMYtjaWGfke6gcztmtY'
    QB_CLIENT_SECRET = 'H75cxmzTruVA2LpU27IyAUzJKJlsNgWHMrJaz3MN'
    QB_COMPANY_ID = '9341455300640805'

    print("📋 Configuration:")
    print(f"Client ID: {QB_CLIENT_ID[:10]}...")
    print(f"Company ID: {QB_COMPANY_ID}")
    print()

    # Test token refresh endpoint
    token_url = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'

    print("🔗 Token Refresh Endpoint:")
    print(f"URL: {token_url}")
    print("Method: POST")
    print("Auth: Basic (Client ID + Client Secret)")
    print()

    # Test with invalid refresh token (to see error format)
    test_data = {
        'grant_type': 'refresh_token',
        'refresh_token': 'invalid_refresh_token'
    }

    print("🧪 Testing with invalid refresh token:")
    try:
        response = requests.post(
            token_url,
            data=test_data,
            auth=(QB_CLIENT_ID, QB_CLIENT_SECRET),
            headers={'Accept': 'application/json'}
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print()

    except Exception as e:
        print(f"Error: {str(e)}")
        print()

def test_qb_api_without_token():
    """Test QuickBooks API without token"""
    print("🔍 Testing QuickBooks API Without Token")
    print("=" * 40)
    print()

    QB_COMPANY_ID = '9341455300640805'
    QB_BASE_URL = 'https://sandbox-quickbooks.api.intuit.com'

    # Test company info endpoint without token
    url = f"{QB_BASE_URL}/v3/company/{QB_COMPANY_ID}/companyinfo/{QB_COMPANY_ID}"

    print("🔗 API Endpoint:")
    print(f"URL: {url}")
    print("Method: GET")
    print("Headers: No Authorization")
    print()

    try:
        response = requests.get(url, headers={'Accept': 'application/json'})

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print()

    except Exception as e:
        print(f"Error: {str(e)}")
        print()

def test_qb_api_with_invalid_token():
    """Test QuickBooks API with invalid token"""
    print("🔍 Testing QuickBooks API With Invalid Token")
    print("=" * 40)
    print()

    QB_COMPANY_ID = '9341455300640805'
    QB_BASE_URL = 'https://sandbox-quickbooks.api.intuit.com'

    # Test company info endpoint with invalid token
    url = f"{QB_BASE_URL}/v3/company/{QB_COMPANY_ID}/companyinfo/{QB_COMPANY_ID}"
    headers = {
        'Authorization': 'Bearer invalid_access_token',
        'Accept': 'application/json'
    }

    print("🔗 API Endpoint:")
    print(f"URL: {url}")
    print("Method: GET")
    print("Headers: Authorization: Bearer invalid_access_token")
    print()

    try:
        response = requests.get(url, headers=headers)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print()

    except Exception as e:
        print(f"Error: {str(e)}")
        print()

def show_troubleshooting_steps():
    """Show troubleshooting steps for 401 error"""
    print("🐛 Troubleshooting 401 Unauthorized Error")
    print("=" * 45)
    print()

    steps = [
        "1. Check if access token exists in session",
        "2. Verify access token is not expired",
        "3. Try refreshing the access token",
        "4. Reconnect to QuickBooks if refresh fails",
        "5. Check QuickBooks app permissions",
        "6. Verify sandbox company ID is correct"
    ]

    for step in steps:
        print(f"   {step}")
    print()

    print("🔧 Quick Fixes:")
    print("   • Click 'Connect to QB' button to re-authenticate")
    print("   • Check if QuickBooks app is properly configured")
    print("   • Verify sandbox company has the correct permissions")
    print("   • Try disconnecting and reconnecting")
    print()

def show_oauth_flow():
    """Show OAuth flow for reconnection"""
    print("🔐 QuickBooks OAuth Flow")
    print("=" * 25)
    print()

    print("1. User clicks 'Connect to QB'")
    print("2. System generates OAuth URL")
    print("3. User redirected to QuickBooks")
    print("4. User authorizes the app")
    print("5. QuickBooks redirects back with code")
    print("6. System exchanges code for tokens")
    print("7. Tokens stored in session")
    print("8. API calls use access token")
    print()

    print("🔄 Token Refresh Flow:")
    print("1. Access token expires (usually 1 hour)")
    print("2. System detects expired token")
    print("3. System uses refresh token to get new access token")
    print("4. New tokens stored in session")
    print("5. API call retried with new token")
    print()

def main():
    """Main function"""
    print("🧪 QuickBooks 401 Error Debug Tool")
    print("=" * 40)
    print()

    test_qb_token_refresh()
    test_qb_api_without_token()
    test_qb_api_with_invalid_token()
    show_troubleshooting_steps()
    show_oauth_flow()

    print("🎯 Next Steps:")
    print("1. Go to QB Admin page: /quickbooks-admin")
    print("2. Click 'Connect to QB' to re-authenticate")
    print("3. Complete OAuth flow in browser")
    print("4. Test connection again")
    print("5. Check sync operations")

if __name__ == "__main__":
    main()
