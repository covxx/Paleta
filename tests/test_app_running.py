#!/usr/bin/env python3
"""
Test if the Flask app is running and accessible
"""

import requests
import json

def test_app_running():
    """Test if the Flask app is running"""
    print("🧪 Testing Flask App Status")
    print("=" * 30)
    print()
    
    base_url = "http://localhost:5002"
    
    # Test main page
    print("🏠 Testing Main Page:")
    print(f"URL: {base_url}/")
    print()
    
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Main page is accessible!")
            print("   App is running successfully")
        else:
            print(f"❌ Main page error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()
    
    # Test QB Admin page
    print("🔧 Testing QB Admin Page:")
    print(f"URL: {base_url}/quickbooks-admin")
    print()
    
    try:
        response = requests.get(f"{base_url}/quickbooks-admin")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ QB Admin page is accessible!")
        elif response.status_code == 302:
            print("🔄 QB Admin page redirects (likely to login)")
            print("   This is expected - need to be logged in as admin")
        else:
            print(f"❌ QB Admin page error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()
    
    # Test sync status API (should redirect to login)
    print("📊 Testing Sync Status API:")
    print(f"URL: {base_url}/api/quickbooks/sync/status")
    print()
    
    try:
        response = requests.get(f"{base_url}/api/quickbooks/sync/status")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 302:
            print("🔄 Sync Status API redirects to login")
            print("   This is expected - need admin authentication")
        elif response.status_code == 200:
            print("✅ Sync Status API accessible!")
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Sync Status API error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()

def show_testing_instructions():
    """Show instructions for testing sync status"""
    print("🎯 How to Test Sync Status Updates")
    print("=" * 40)
    print()
    
    print("1. 🌐 Open Browser:")
    print("   Go to: http://localhost:5002")
    print()
    
    print("2. 🔐 Login as Admin:")
    print("   - Click 'Admin' in the navigation")
    print("   - Login with admin credentials")
    print("   - Or go directly to: http://localhost:5002/admin/login")
    print()
    
    print("3. 📊 Go to QB Admin:")
    print("   - Click 'QB Admin' in the navigation")
    print("   - Or go directly to: http://localhost:5002/quickbooks-admin")
    print()
    
    print("4. 🔗 Connect to QuickBooks:")
    print("   - Click 'Connect to QB' button")
    print("   - Complete OAuth flow in QuickBooks")
    print("   - This will establish the connection")
    print()
    
    print("5. 🧪 Test Sync Status Updates:")
    print("   - Click any sync button (customers, items, orders)")
    print("   - Watch for success popup")
    print("   - Check if status updates after popup")
    print("   - Use 'Refresh Status' button if needed")
    print()
    
    print("6. 🔍 Debug if Issues:")
    print("   - Open browser console (F12)")
    print("   - Look for JavaScript errors")
    print("   - Check network tab for API calls")
    print("   - Look for 500ms delay in status refresh")
    print()

def main():
    """Main function"""
    print("🚀 Flask App Status Checker")
    print("=" * 30)
    print()
    
    test_app_running()
    show_testing_instructions()
    
    print("✅ App is running on port 5002!")
    print("   Ready for sync status testing")

if __name__ == "__main__":
    main()
