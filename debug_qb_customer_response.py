#!/usr/bin/env python3
"""
Debug QuickBooks customer response structure
"""

import os
import requests
import json
from urllib.parse import quote

# QuickBooks Configuration
QB_CLIENT_ID = 'ABUW0U3AsMTGyq7bb1ujpj17IodZlrGkMYtjaWGfke6gcztmtY'
QB_CLIENT_SECRET = 'H75cxmzTruVA2LpU27IyAUzJKJlsNgWHMrJaz3MN'
QB_COMPANY_ID = '9341455300640805'
QB_BASE_URL = 'https://sandbox-quickbooks.api.intuit.com'

def test_customer_query_structure():
    """Test the customer query and show expected response structure"""
    print("🔍 QuickBooks Customer Response Structure Analysis")
    print("=" * 60)
    print()
    
    # Test different customer queries
    queries = [
        {
            'name': 'All Customers',
            'query': 'SELECT * FROM Customer',
            'description': 'Get all customer fields'
        },
        {
            'name': 'Customer Basic Info',
            'query': 'SELECT Id, Name, PrimaryEmailAddr, PrimaryPhone FROM Customer',
            'description': 'Get basic customer information'
        },
        {
            'name': 'Customer with Address',
            'query': 'SELECT Id, Name, PrimaryEmailAddr, PrimaryPhone, BillAddr, ShipAddr FROM Customer',
            'description': 'Get customer with address information'
        }
    ]
    
    for query_test in queries:
        print(f"📋 {query_test['name']}:")
        print(f"   Query: {query_test['query']}")
        print(f"   Description: {query_test['description']}")
        print(f"   URL: {QB_BASE_URL}/v3/company/{QB_COMPANY_ID}/query?query={quote(query_test['query'])}&minorversion=75")
        print()

def show_expected_customer_response():
    """Show expected customer response structure"""
    print("📄 Expected Customer Response Structure:")
    print("=" * 50)
    print()
    
    expected_response = {
        "QueryResponse": {
            "Customer": [
                {
                    "Id": "1",
                    "Name": "John Doe",
                    "PrimaryEmailAddr": {
                        "Address": "john.doe@example.com"
                    },
                    "PrimaryPhone": {
                        "FreeFormNumber": "(555) 123-4567"
                    },
                    "BillAddr": {
                        "Name": "John Doe",
                        "Line1": "123 Main St",
                        "Line2": "Suite 100",
                        "City": "Anytown",
                        "CountrySubDivisionCode": "CA",
                        "PostalCode": "12345",
                        "Country": "USA"
                    },
                    "ShipAddr": {
                        "Name": "John Doe",
                        "Line1": "123 Main St",
                        "Line2": "Suite 100",
                        "City": "Anytown",
                        "CountrySubDivisionCode": "CA",
                        "PostalCode": "12345",
                        "Country": "USA"
                    },
                    "PaymentMethodRef": {
                        "name": "Check"
                    }
                }
            ],
            "maxResults": 1,
            "startPosition": 1
        }
    }
    
    print("📋 Full Customer Response:")
    print(json.dumps(expected_response, indent=2))
    print()

def show_field_mapping():
    """Show current field mapping"""
    print("🔗 Current Field Mapping:")
    print("=" * 30)
    print()
    
    mappings = [
        ("QB Field", "Local Field", "Example Value"),
        ("Name", "name", "John Doe"),
        ("PrimaryEmailAddr.Address", "email", "john.doe@example.com"),
        ("PrimaryPhone.FreeFormNumber", "phone", "(555) 123-4567"),
        ("Id", "quickbooks_id", "1"),
        ("BillAddr.Name", "bill_to_name", "John Doe"),
        ("BillAddr.Line1", "bill_to_address1", "123 Main St"),
        ("BillAddr.City", "bill_to_city", "Anytown"),
        ("BillAddr.CountrySubDivisionCode", "bill_to_state", "CA"),
        ("BillAddr.PostalCode", "bill_to_zip", "12345"),
        ("ShipAddr.Name", "ship_to_name", "John Doe"),
        ("ShipAddr.Line1", "ship_to_address1", "123 Main St"),
        ("ShipAddr.City", "ship_to_city", "Anytown"),
        ("ShipAddr.CountrySubDivisionCode", "ship_to_state", "CA"),
        ("ShipAddr.PostalCode", "ship_to_zip", "12345")
    ]
    
    for mapping in mappings:
        if mapping[0] == "QB Field":
            print(f"{'QB Field':<25} {'Local Field':<20} {'Example Value'}")
            print("-" * 60)
        else:
            print(f"{mapping[0]:<25} {mapping[1]:<20} {mapping[2]}")

def show_alternative_field_mappings():
    """Show alternative field mappings that might work"""
    print("\n🔄 Alternative Field Mappings:")
    print("=" * 35)
    print()
    
    alternatives = [
        {
            'field': 'Name',
            'alternatives': ['DisplayName', 'CompanyName', 'GivenName', 'FamilyName'],
            'description': 'Customer name field alternatives'
        },
        {
            'field': 'PrimaryEmailAddr.Address',
            'alternatives': ['EmailAddr.Address', 'PrimaryEmailAddr', 'Email'],
            'description': 'Email field alternatives'
        },
        {
            'field': 'PrimaryPhone.FreeFormNumber',
            'alternatives': ['Phone.FreeFormNumber', 'PrimaryPhone', 'Phone'],
            'description': 'Phone field alternatives'
        }
    ]
    
    for alt in alternatives:
        print(f"📋 {alt['field']}:")
        print(f"   Description: {alt['description']}")
        print(f"   Alternatives: {', '.join(alt['alternatives'])}")
        print()

def show_debugging_steps():
    """Show debugging steps"""
    print("🐛 Debugging Steps:")
    print("=" * 20)
    print()
    
    steps = [
        "1. Check the actual QuickBooks API response",
        "2. Verify field names in the response",
        "3. Test with a simple customer query",
        "4. Compare expected vs actual response structure",
        "5. Update field mapping if needed"
    ]
    
    for step in steps:
        print(f"   {step}")
    print()
    
    print("🔧 Debug Commands:")
    print("   # Test customer query directly")
    print("   curl -X GET 'https://sandbox-quickbooks.api.intuit.com/v3/company/9341455300640805/query?query=SELECT%20*%20FROM%20Customer&minorversion=75' \\")
    print("     -H 'Authorization: Bearer {access_token}' \\")
    print("     -H 'Accept: application/json'")
    print()

def main():
    """Main function"""
    test_customer_query_structure()
    show_expected_customer_response()
    show_field_mapping()
    show_alternative_field_mappings()
    show_debugging_steps()
    
    print("🎯 Next Steps:")
    print("1. Check the actual API response structure")
    print("2. Verify if 'Name' field exists in the response")
    print("3. Try alternative field names if needed")
    print("4. Update the field mapping accordingly")

if __name__ == "__main__":
    main()
