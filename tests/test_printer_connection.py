#!/usr/bin/env python3
"""
Simple printer connection test script
Helps diagnose network connectivity issues with printers
"""

import socket
import time

def test_printer_connection(ip, port=9100):
    """Test basic connectivity to a printer"""
    print(f"Testing connection to {ip}:{port}")
    
    try:
        # Test basic socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        
        print(f"Attempting to connect...")
        sock.connect((ip, port))
        print(f"✅ SUCCESS: Connected to {ip}:{port}")
        
        # Send a simple test command
        test_command = "~HS\n"  # Host status command
        print(f"Sending test command: {test_command.strip()}")
        sock.send(test_command.encode())
        
        # Try to receive response (some printers don't respond)
        try:
            response = sock.recv(1024)
            print(f"Response: {response.decode()}")
        except socket.timeout:
            print("No response received (this is normal for some printers)")
        
        sock.close()
        return True
        
    except socket.timeout:
        print(f"❌ TIMEOUT: Connection to {ip}:{port} timed out")
        print("   - Printer may be offline")
        print("   - Network may be slow")
        return False
    except ConnectionRefusedError:
        print(f"❌ REFUSED: Connection to {ip}:{port} was refused")
        print("   - Printer may be offline")
        print("   - Port may be blocked by firewall")
        print("   - IP address may be incorrect")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_all_printers():
    """Test all configured printers"""
    import requests
    
    try:
        # Get printers from the API
        response = requests.get('http://localhost:5001/api/printers')
        printers = response.json()
        
        print(f"Found {len(printers)} configured printers\n")
        
        for printer in printers:
            print(f"=== Testing {printer['name']} ===")
            test_printer_connection(printer['ip_address'], printer['port'])
            print()
            
    except Exception as e:
        print(f"Error getting printers from API: {e}")
        print("Make sure the Flask server is running on port 5001")

if __name__ == "__main__":
    print("🔌 Printer Connection Test Tool")
    print("=" * 40)
    
    # Test specific printer if IP is provided
    import sys
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 9100
        test_printer_connection(ip, port)
    else:
        # Test all configured printers
        test_all_printers()
    
    print("\n💡 Troubleshooting Tips:")
    print("1. Make sure the printer is powered on and connected to the network")
    print("2. Verify the IP address is correct (check printer's network settings)")
    print("3. Check if there's a firewall blocking port 9100")
    print("4. Try pinging the printer IP address first")
    print("5. Ensure the printer supports network printing on port 9100")
