#!/usr/bin/env python3
"""
Test order creation and QuickBooks sync functionality
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone

# Add the current directory to Python path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_order_creation():
    """Test creating an order through the API"""
    print("🧪 Testing Order Creation and QuickBooks Sync")
    print("=" * 50)
    print()

    # Test order data
    order_data = {
        "customer_id": 1,  # Assuming customer ID 1 exists
        "order_date": datetime.now().strftime('%Y-%m-%d'),
        "notes": "Test order for QuickBooks sync",
        "order_items": [
            {
                "item_id": 1,  # Assuming item ID 1 exists
                "quantity_ordered": 2,
                "unit_price": 25.00,
                "notes": "Test item for QB sync"
            }
        ]
    }

    print("📋 Test Order Data:")
    print(json.dumps(order_data, indent=2))
    print()

    # API endpoint for creating orders
    create_order_url = "http://localhost:5001/api/orders"

    print("🔗 Order Creation API:")
    print(f"   POST {create_order_url}")
    print(f"   Data: {json.dumps(order_data)}")
    print()

def test_quickbooks_sync():
    """Test QuickBooks sync for an order"""
    print("🔄 Testing QuickBooks Sync")
    print("=" * 30)
    print()

    # Test sync endpoint
    order_id = 1  # Assuming order ID 1 exists
    sync_url = f"http://localhost:5001/api/orders/{order_id}/sync-quickbooks"

    print("🔗 QuickBooks Sync API:")
    print(f"   POST {sync_url}")
    print("   Headers: Content-Type: application/json")
    print()

def show_quickbooks_invoice_structure():
    """Show the QuickBooks invoice data structure"""
    print("📄 QuickBooks Invoice Data Structure:")
    print("=" * 40)
    print()

    invoice_data = {
        "CustomerRef": {
            "value": "1"  # Customer QuickBooks ID
        },
        "Line": [
            {
                "DetailType": "SalesItemLineDetail",
                "Amount": 50.00,
                "SalesItemLineDetail": {
                    "ItemRef": {
                        "value": "1"  # Item QuickBooks ID
                    },
                    "Qty": 2,
                    "UnitPrice": 25.00
                },
                "Description": "Test item for QB sync"
            }
        ],
        "TotalAmt": 50.00,
        "TxnDate": "2025-01-05",
        "DocNumber": "ORD-001",
        "PrivateNote": "Test order for QuickBooks sync"
    }

    print("📋 Invoice Data Structure:")
    print(json.dumps(invoice_data, indent=2))
    print()

def show_testing_steps():
    """Show step-by-step testing instructions"""
    print("🧪 Testing Steps:")
    print("=" * 20)
    print()

    steps = [
        "1. Ensure QuickBooks connection is working",
        "2. Import customers and items from QuickBooks",
        "3. Create a test order in the system",
        "4. Verify order has items and customer",
        "5. Sync the order to QuickBooks",
        "6. Check QuickBooks for the created invoice"
    ]

    for step in steps:
        print(f"   {step}")
    print()

    print("🔧 Prerequisites:")
    print("   ✅ QuickBooks OAuth connection established")
    print("   ✅ Customers imported from QuickBooks")
    print("   ✅ Items imported from QuickBooks")
    print("   ✅ Order created with valid customer and items")
    print()

def show_curl_commands():
    """Show curl commands for testing"""
    print("🔧 CURL Commands for Testing:")
    print("=" * 35)
    print()

    print("📋 Create Order:")
    print("curl -X POST http://localhost:5001/api/orders \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "customer_id": 1,')
    print('    "order_date": "2025-01-05",')
    print('    "notes": "Test order for QB sync",')
    print('    "order_items": [')
    print('      {')
    print('        "item_id": 1,')
    print('        "quantity_ordered": 2,')
    print('        "unit_price": 25.00')
    print('      }')
    print('    ]')
    print("  }'")
    print()

    print("🔄 Sync Order to QuickBooks:")
    print("curl -X POST http://localhost:5001/api/orders/1/sync-quickbooks \\")
    print("  -H 'Content-Type: application/json'")
    print()

def show_expected_responses():
    """Show expected API responses"""
    print("📄 Expected API Responses:")
    print("=" * 30)
    print()

    print("✅ Successful Order Creation:")
    order_response = {
        "success": True,
        "order_id": 1,
        "order_number": "ORD-001",
        "message": "Order created successfully"
    }
    print(json.dumps(order_response, indent=2))
    print()

    print("✅ Successful QuickBooks Sync:")
    sync_response = {
        "success": True,
        "quickbooks_id": "123",
        "message": "Order ORD-001 synced to QuickBooks as Invoice 123"
    }
    print(json.dumps(sync_response, indent=2))
    print()

    print("❌ Error Responses:")
    error_responses = [
        {
            "error": "Customer not synced to QuickBooks. Please import customers first.",
            "status": 400
        },
        {
            "error": "Item 'Test Item' not synced to QuickBooks. Please import items first.",
            "status": 400
        },
        {
            "error": "Order has no items to sync",
            "status": 400
        }
    ]

    for error in error_responses:
        print(f"   {json.dumps(error)}")
    print()

def show_troubleshooting():
    """Show troubleshooting tips"""
    print("🐛 Troubleshooting:")
    print("=" * 20)
    print()

    issues = [
        {
            "issue": "Customer not synced to QuickBooks",
            "solution": "Import customers from QuickBooks first"
        },
        {
            "issue": "Item not synced to QuickBooks",
            "solution": "Import items from QuickBooks first"
        },
        {
            "issue": "Order has no items",
            "solution": "Add items to the order before syncing"
        },
        {
            "issue": "QuickBooks API error",
            "solution": "Check OAuth connection and API credentials"
        }
    ]

    for issue in issues:
        print(f"📋 {issue['issue']}:")
        print(f"   Solution: {issue['solution']}")
        print()

def main():
    """Main function"""
    test_order_creation()
    test_quickbooks_sync()
    show_quickbooks_invoice_structure()
    show_testing_steps()
    show_curl_commands()
    show_expected_responses()
    show_troubleshooting()

    print("🎯 Ready to Test!")
    print("1. Start the app: source venv/bin/activate && python app.py")
    print("2. Import customers and items from QuickBooks")
    print("3. Create a test order")
    print("4. Sync the order to QuickBooks")
    print("5. Check QuickBooks for the invoice")

if __name__ == "__main__":
    main()
