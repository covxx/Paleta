#!/usr/bin/env python3
"""
Test QuickBooks Sync Status Functionality
"""

import os
import sys
import requests
import json
import time

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sync_status_api():
    """Test the sync status API endpoint"""
    print("🧪 Testing QuickBooks Sync Status API")
    print("=" * 40)
    print()
    
    base_url = "http://localhost:5002"
    
    # Test sync status endpoint
    print("📊 Testing Sync Status Endpoint:")
    print(f"URL: {base_url}/api/quickbooks/sync/status")
    print("Method: GET")
    print()
    
    try:
        response = requests.get(f"{base_url}/api/quickbooks/sync/status")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Sync Status API Working!")
                print(f"   Customers: {data.get('customer_status')}")
                print(f"   Items: {data.get('item_status')}")
                print(f"   Pending Orders: {data.get('pending_orders')}")
            else:
                print("❌ Sync Status API Error:", data.get('error'))
        else:
            print("❌ HTTP Error:", response.status_code)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()

def test_sync_log_api():
    """Test the sync log API endpoint"""
    print("📝 Testing Sync Log API")
    print("=" * 25)
    print()
    
    base_url = "http://localhost:5002"
    
    print("📊 Testing Sync Log Endpoint:")
    print(f"URL: {base_url}/api/quickbooks/sync/log")
    print("Method: GET")
    print()
    
    try:
        response = requests.get(f"{base_url}/api/quickbooks/sync/log")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Sync Log API Working!")
                print(f"   Logs Count: {len(data.get('logs', []))}")
                for log in data.get('logs', [])[:3]:  # Show first 3 logs
                    print(f"   - {log.get('type')}: {log.get('status')} - {log.get('message')}")
            else:
                print("❌ Sync Log API Error:", data.get('error'))
        else:
            print("❌ HTTP Error:", response.status_code)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()

def test_sync_operations():
    """Test sync operations"""
    print("🔄 Testing Sync Operations")
    print("=" * 25)
    print()
    
    base_url = "http://localhost:5002"
    
    # Test customer sync
    print("👥 Testing Customer Sync:")
    print(f"URL: {base_url}/api/quickbooks/sync/customers")
    print("Method: POST")
    print()
    
    try:
        response = requests.post(f"{base_url}/api/quickbooks/sync/customers")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Customer Sync Successful!")
            else:
                print("❌ Customer Sync Failed:", data.get('error'))
        else:
            print("❌ HTTP Error:", response.status_code)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()
    
    # Wait a moment then check status
    print("⏳ Waiting 2 seconds then checking status...")
    time.sleep(2)
    
    try:
        response = requests.get(f"{base_url}/api/quickbooks/sync/status")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("📊 Updated Status:")
                print(f"   Customers: {data.get('customer_status')}")
                print(f"   Items: {data.get('item_status')}")
                print(f"   Pending Orders: {data.get('pending_orders')}")
    except Exception as e:
        print(f"❌ Error checking status: {str(e)}")
    print()

def show_troubleshooting_tips():
    """Show troubleshooting tips for sync status issues"""
    print("🔧 Troubleshooting Sync Status Issues")
    print("=" * 40)
    print()
    
    tips = [
        "1. Check if the Flask app is running on localhost:5000",
        "2. Verify QuickBooks connection is established",
        "3. Check browser console for JavaScript errors",
        "4. Ensure sync operations are completing successfully",
        "5. Check Flask app logs for backend errors",
        "6. Verify database has customers/items to sync",
        "7. Test API endpoints directly with curl/Postman"
    ]
    
    for tip in tips:
        print(f"   {tip}")
    print()
    
    print("🧪 Manual Testing Commands:")
    print("   curl http://localhost:5000/api/quickbooks/sync/status")
    print("   curl -X POST http://localhost:5000/api/quickbooks/sync/customers")
    print("   curl http://localhost:5000/api/quickbooks/sync/log")
    print()

def main():
    """Main function"""
    print("🧪 QuickBooks Sync Status Test Tool")
    print("=" * 40)
    print()
    
    test_sync_status_api()
    test_sync_log_api()
    test_sync_operations()
    show_troubleshooting_tips()
    
    print("🎯 Next Steps:")
    print("1. Start the Flask app: python app.py")
    print("2. Go to QB Admin: http://localhost:5000/quickbooks-admin")
    print("3. Test sync operations and watch status updates")
    print("4. Check browser console for any JavaScript errors")
    print("5. Use the 'Refresh Status' button to manually update")

if __name__ == "__main__":
    main()
