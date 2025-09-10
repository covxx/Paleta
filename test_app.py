#!/usr/bin/env python3
"""
Simple test script to check if Flask app can start without errors
"""

import sys
import os

# Add configs to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'configs'))

try:
    print("1. Testing basic imports...")
    import flask
    print("✅ Flask imported")
    
    import flask_sqlalchemy
    print("✅ Flask-SQLAlchemy imported")
    
    print("2. Testing config import...")
    import config
    print("✅ Config imported")
    
    print("3. Testing app import...")
    import app
    print("✅ App imported")
    
    print("4. Testing app creation...")
    with app.app.app_context():
        print("✅ App context works")
    
    print("5. Testing static file serving...")
    with app.app.test_client() as client:
        response = client.get('/static/css/design-system.css')
        print(f"✅ CSS file response: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ CSS file error: {response.data}")
    
    print("\n✅ All tests passed! App should work correctly.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
