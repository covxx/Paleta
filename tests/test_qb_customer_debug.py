#!/usr/bin/env python3
"""
Test QuickBooks customer import to debug field mapping issues
"""

import os
import sys
import json

# Add the current directory to Python path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_customer_field_mapping():
    """Test customer field mapping with sample data"""
    print("🧪 Testing Customer Field Mapping")
    print("=" * 40)
    print()

    # Sample QuickBooks customer response (what we expect)
    sample_qb_response = {
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
                    "EmailAddr": {
                        "Address": "john.doe@example.com"
                    },
                    "PrimaryPhone": {
                        "FreeFormNumber": "(555) 123-4567"
                    },
                    "Phone": {
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
                    }
                }
            ]
        }
    }

    print("📋 Sample QuickBooks Response:")
    print(json.dumps(sample_qb_response, indent=2))
    print()

    # Test field extraction
    for qb_customer in sample_qb_response.get('QueryResponse', {}).get('Customer', []):
        print("🔍 Field Extraction Test:")
        print("-" * 25)

        # Test different name field options
        name_options = [
            ('Name', qb_customer.get('Name')),
            ('DisplayName', qb_customer.get('DisplayName')),
            ('CompanyName', qb_customer.get('CompanyName'))
        ]

        print("📝 Name Field Options:")
        for field_name, value in name_options:
            print(f"   {field_name}: '{value}'")

        # Select the best name
        selected_name = (qb_customer.get('Name') or
                        qb_customer.get('DisplayName') or
                        qb_customer.get('CompanyName') or
                        'Unknown Customer')
        print(f"   ✅ Selected: '{selected_name}'")
        print()

        # Test email field options
        email_options = [
            ('PrimaryEmailAddr.Address', qb_customer.get('PrimaryEmailAddr', {}).get('Address')),
            ('EmailAddr.Address', qb_customer.get('EmailAddr', {}).get('Address'))
        ]

        print("📧 Email Field Options:")
        for field_name, value in email_options:
            print(f"   {field_name}: '{value}'")

        # Select the best email
        selected_email = (qb_customer.get('PrimaryEmailAddr', {}).get('Address', '') or
                         qb_customer.get('EmailAddr', {}).get('Address', ''))
        print(f"   ✅ Selected: '{selected_email}'")
        print()

        # Test phone field options
        phone_options = [
            ('PrimaryPhone.FreeFormNumber', qb_customer.get('PrimaryPhone', {}).get('FreeFormNumber')),
            ('Phone.FreeFormNumber', qb_customer.get('Phone', {}).get('FreeFormNumber'))
        ]

        print("📞 Phone Field Options:")
        for field_name, value in phone_options:
            print(f"   {field_name}: '{value}'")

        # Select the best phone
        selected_phone = (qb_customer.get('PrimaryPhone', {}).get('FreeFormNumber', '') or
                         qb_customer.get('Phone', {}).get('FreeFormNumber', ''))
        print(f"   ✅ Selected: '{selected_phone}'")
        print()

        # Show final customer data
        customer_data = {
            'name': selected_name,
            'email': selected_email,
            'phone': selected_phone,
            'quickbooks_id': qb_customer.get('Id', ''),
            'bill_to_name': qb_customer.get('BillAddr', {}).get('Name', ''),
            'bill_to_address1': qb_customer.get('BillAddr', {}).get('Line1', ''),
            'bill_to_city': qb_customer.get('BillAddr', {}).get('City', ''),
            'bill_to_state': qb_customer.get('BillAddr', {}).get('CountrySubDivisionCode', ''),
            'bill_to_zip': qb_customer.get('BillAddr', {}).get('PostalCode', ''),
            'ship_to_name': qb_customer.get('ShipAddr', {}).get('Name', ''),
            'ship_to_address1': qb_customer.get('ShipAddr', {}).get('Line1', ''),
            'ship_to_city': qb_customer.get('ShipAddr', {}).get('City', ''),
            'ship_to_state': qb_customer.get('ShipAddr', {}).get('CountrySubDivisionCode', ''),
            'ship_to_zip': qb_customer.get('ShipAddr', {}).get('PostalCode', '')
        }

        print("📋 Final Customer Data:")
        for key, value in customer_data.items():
            print(f"   {key}: '{value}'")
        print()

def test_empty_field_scenarios():
    """Test scenarios where fields might be empty"""
    print("🔍 Testing Empty Field Scenarios")
    print("=" * 35)
    print()

    # Test with minimal data
    minimal_customer = {
        "Id": "2",
        "DisplayName": "Jane Smith"
        # Missing Name, email, phone
    }

    print("📋 Minimal Customer Data:")
    print(json.dumps(minimal_customer, indent=2))
    print()

    # Test field extraction with fallbacks
    name = (minimal_customer.get('Name') or
            minimal_customer.get('DisplayName') or
            minimal_customer.get('CompanyName') or
            'Unknown Customer')

    email = (minimal_customer.get('PrimaryEmailAddr', {}).get('Address', '') or
             minimal_customer.get('EmailAddr', {}).get('Address', ''))

    phone = (minimal_customer.get('PrimaryPhone', {}).get('FreeFormNumber', '') or
             minimal_customer.get('Phone', {}).get('FreeFormNumber', ''))

    print("🔍 Field Extraction Results:")
    print(f"   Name: '{name}'")
    print(f"   Email: '{email}'")
    print(f"   Phone: '{phone}'")
    print()

def show_debugging_tips():
    """Show debugging tips"""
    print("🐛 Debugging Tips:")
    print("=" * 20)
    print()

    tips = [
        "1. Check the Flask console output for DEBUG messages",
        "2. Look for 'DEBUG: QB Customer data:' in the logs",
        "3. Compare the actual response with expected structure",
        "4. Verify if QuickBooks sandbox has test customers",
        "5. Check if customers have the expected field names"
    ]

    for tip in tips:
        print(f"   {tip}")
    print()

    print("🔧 Next Steps:")
    print("   1. Run the customer import in the app")
    print("   2. Check the console output for DEBUG messages")
    print("   3. Compare actual vs expected field names")
    print("   4. Update field mapping if needed")

def main():
    """Main function"""
    test_customer_field_mapping()
    test_empty_field_scenarios()
    show_debugging_tips()

if __name__ == "__main__":
    main()
