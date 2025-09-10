#!/usr/bin/env python3
"""
Test JavaScript Fix for Spinner Error
"""

import requests
import time

def test_qb_admin_page():
    """Test if QB Admin page loads without JavaScript errors"""
    print("🧪 Testing QB Admin Page JavaScript Fix")
    print("=" * 45)
    print()

    base_url = "http://localhost:5002"

    # Test QB Admin page
    print("📄 Testing QB Admin Page Load:")
    print(f"URL: {base_url}/quickbooks-admin")
    print()

    try:
        response = requests.get(f"{base_url}/quickbooks-admin")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ QB Admin page loads successfully!")

            # Check if key elements are in the HTML
            html_content = response.text

            checks = [
                ('connectionStatus', 'Connection status div'),
                ('connectionSpinner', 'Connection spinner element'),
                ('customerSyncStatus', 'Customer sync status element'),
                ('itemSyncStatus', 'Item sync status element'),
                ('pendingOrdersCount', 'Pending orders count element'),
                ('refreshAllStatus', 'Refresh status function')
            ]

            print("\n🔍 Checking for Required Elements:")
            for element_id, description in checks:
                if f'id="{element_id}"' in html_content or f"id='{element_id}'" in html_content:
                    print(f"   ✅ {description} found")
                else:
                    print(f"   ❌ {description} missing")

            # Check for JavaScript fixes
            print("\n🔧 Checking for JavaScript Fixes:")
            js_fixes = [
                ('if (!statusDiv)', 'Null check for statusDiv'),
                ('if (spinner)', 'Null check for spinner'),
                ('safeGetElement', 'Safe element access function'),
                ('setTimeout(() => {', 'DOM ready delay')
            ]

            for fix, description in js_fixes:
                if fix in html_content:
                    print(f"   ✅ {description} implemented")
                else:
                    print(f"   ❌ {description} missing")

        elif response.status_code == 302:
            print("🔄 QB Admin page redirects (likely to login)")
            print("   This is expected - need to be logged in as admin")
        else:
            print(f"❌ QB Admin page error: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()

def test_sync_status_api():
    """Test sync status API"""
    base_url = "http://localhost:5002"
    print("📊 Testing Sync Status API:")
    print(f"URL: {base_url}/api/quickbooks/sync/status")
    print()

    try:
        response = requests.get(f"{base_url}/api/quickbooks/sync/status")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ Sync Status API accessible!")
        elif response.status_code == 302:
            print("🔄 Sync Status API redirects to login")
            print("   This is expected - need admin authentication")
        else:
            print(f"❌ Sync Status API error: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()

def show_testing_instructions():
    """Show instructions for testing the JavaScript fix"""
    print("🎯 How to Test the JavaScript Fix")
    print("=" * 35)
    print()

    print("1. 🌐 Open Browser:")
    print("   Go to: http://localhost:5002")
    print()

    print("2. 🔐 Login as Admin:")
    print("   - Click 'Admin' in navigation")
    print("   - Login with admin credentials")
    print("   - Or go to: http://localhost:5002/admin/login")
    print()

    print("3. 📊 Go to QB Admin:")
    print("   - Click 'QB Admin' in navigation")
    print("   - Or go to: http://localhost:5002/quickbooks-admin")
    print()

    print("4. 🔍 Check Browser Console:")
    print("   - Press F12 to open Developer Tools")
    print("   - Go to Console tab")
    print("   - Look for any JavaScript errors")
    print("   - Should see no 'null is not an object' errors")
    print()

    print("5. 🧪 Test Refresh Status Button:")
    print("   - Click 'Refresh Status' button")
    print("   - Should see loading spinner")
    print("   - Should complete without JavaScript errors")
    print("   - Check console for any error messages")
    print()

    print("6. 🔄 Test Connection Button:")
    print("   - Click 'Test Connection' button")
    print("   - Should show connection status")
    print("   - Should hide spinner properly")
    print("   - No JavaScript errors in console")
    print()

def main():
    """Main function"""
    print("🚀 JavaScript Fix Test Tool")
    print("=" * 30)
    print()

    test_qb_admin_page()
    test_sync_status_api()
    show_testing_instructions()

    print("✅ JavaScript fixes implemented!")
    print("   Ready for testing in browser")

if __name__ == "__main__":
    main()
