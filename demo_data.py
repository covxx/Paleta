#!/usr/bin/env python3
"""
Demo data script for Inventory Management System
Populates the database with sample items and LOT codes
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Item, Lot, generate_lot_code
from datetime import datetime, timedelta
import random

def create_demo_data():
    """Create sample data for demonstration"""
    
    with app.app_context():
        # Clear existing data
        print("🗑️  Clearing existing data...")
        Lot.query.delete()
        Item.query.delete()
        db.session.commit()
        
        # Create sample items
        print("📦 Creating sample items...")
        
        items = [
            {
                'name': 'Premium Coffee Beans',
                'item_code': 'COFFEE001',
                'gtin': '12345678901234',
                'description': 'Arabica coffee beans, medium roast'
            },
            {
                'name': 'Organic Tea Leaves',
                'item_code': 'TEA002',
                'gtin': '23456789012345',
                'description': 'Green tea leaves, loose leaf'
            },
            {
                'name': 'Raw Honey',
                'item_code': 'HONEY003',
                'gtin': '34567890123456',
                'description': 'Pure wildflower honey, unfiltered'
            },
            {
                'name': 'Whole Grain Flour',
                'item_code': 'FLOUR004',
                'gtin': '45678901234567',
                'description': 'Stone-ground whole wheat flour'
            },
            {
                'name': 'Extra Virgin Olive Oil',
                'item_code': 'OIL005',
                'gtin': '56789012345678',
                'description': 'Cold-pressed olive oil, first harvest'
            }
        ]
        
        created_items = []
        for item_data in items:
            item = Item(**item_data)
            db.session.add(item)
            created_items.append(item)
        
        db.session.commit()
        print(f"✅ Created {len(created_items)} items")
        
        # Create sample LOT codes
        print("🏷️  Creating sample LOT codes...")
        
        lot_count = 0
        for item in created_items:
            # Create 2-4 LOT codes per item
            num_lots = random.randint(2, 4)
            
            for i in range(num_lots):
                # Random expiry date between 30 days and 2 years from now
                days_ahead = random.randint(30, 730)
                expiry_date = datetime.now().date() + timedelta(days=days_ahead)
                
                # Random quantity between 10 and 1000
                quantity = random.randint(10, 1000)
                
                lot = Lot(
                    lot_code=generate_lot_code(item.id),
                    item_id=item.id,
                    quantity=quantity,
                    expiry_date=expiry_date
                )
                db.session.add(lot)
                lot_count += 1
        
        db.session.commit()
        print(f"✅ Created {lot_count} LOT codes")
        
        print("\n🎉 Demo data created successfully!")
        print(f"📊 Database now contains:")
        print(f"   - {len(created_items)} items")
        print(f"   - {lot_count} LOT codes")
        print("\n🚀 You can now start the application and see the sample data!")

if __name__ == '__main__':
    print("🏭 Inventory Management System - Demo Data Creator")
    print("=" * 50)
    
    # Check if database exists
    db_path = 'instance/inventory.db'
    if not os.path.exists(db_path):
        print("❌ Database not found. Please run the application first to create it.")
        sys.exit(1)
    
    try:
        create_demo_data()
    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        sys.exit(1)
