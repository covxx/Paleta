#!/usr/bin/env python3
"""
Database initialization script with performance optimizations
"""

import os
import sys
from app import app, db, Item, Vendor, Lot, AdminUser, Printer, PrintJob

def init_database():
    """Initialize the database with all tables and indexes"""
    with app.app_context():
        # Drop all tables if they exist
        db.drop_all()
        
        # Create all tables with indexes
        db.create_all()
        
        # Create default admin user
        from werkzeug.security import generate_password_hash
        admin_user = AdminUser(
            email='admin@inventory.com',
            password_hash=generate_password_hash('admin123'),
            first_name='Admin',
            last_name='User',
            is_super_admin=True
        )
        db.session.add(admin_user)
        
        # Create sample items
        sample_items = [
            Item(name='Coffee Beans', description='Premium Arabica coffee beans', item_code='COFFEE001', gtin='12345678901234', category='Beverages'),
            Item(name='Green Tea', description='Organic green tea leaves', item_code='TEA002', gtin='12345678901235', category='Beverages'),
            Item(name='Honey', description='Pure wildflower honey', item_code='HONEY003', gtin='12345678901236', category='Sweeteners'),
            Item(name='Flour', description='All-purpose wheat flour', item_code='FLOUR004', gtin='12345678901237', category='Baking'),
            Item(name='Olive Oil', description='Extra virgin olive oil', item_code='OIL005', gtin='12345678901238', category='Cooking')
        ]
        
        for item in sample_items:
            db.session.add(item)
        
        # Create sample vendors
        sample_vendors = [
            Vendor(name='Fresh Foods Co.', contact_person='John Smith', email='john@freshfoods.com', phone='555-0101', address='123 Farm Road, Green Valley, CA 90210'),
            Vendor(name='Organic Suppliers', contact_person='Sarah Johnson', email='sarah@organic.com', phone='555-0102', address='456 Organic Lane, Eco City, CA 90211'),
            Vendor(name='Bulk Distributors', contact_person='Mike Brown', email='mike@bulk.com', phone='555-0103', address='789 Warehouse Blvd, Industrial Park, CA 90212')
        ]
        
        for vendor in sample_vendors:
            db.session.add(vendor)
        
        # Create sample lots
        from datetime import datetime, timedelta, timezone
        current_date = datetime.now(timezone.utc).date()
        
        sample_lots = [
            Lot(lot_code='LOT0001202509041130BF90', item_id=1, vendor_id=1, quantity=50, unit_type='cases', 
                expiry_date=current_date + timedelta(days=10), receiving_date=current_date),
            Lot(lot_code='LOT0002202509041131CG91', item_id=2, vendor_id=2, quantity=25, unit_type='pounds', 
                expiry_date=current_date + timedelta(days=10), receiving_date=current_date),
            Lot(lot_code='LOT0003202509041132DH92', item_id=3, vendor_id=1, quantity=100, unit_type='cases', 
                expiry_date=current_date + timedelta(days=10), receiving_date=current_date)
        ]
        
        for lot in sample_lots:
            db.session.add(lot)
        
        # Create sample printer
        sample_printer = Printer(
            name='Main Label Printer',
            ip_address='192.168.1.100',
            port=9100,
            printer_type='zebra',
            label_width=4.0,
            label_height=2.0,
            dpi=203,
            status='online'
        )
        db.session.add(sample_printer)
        
        # Commit all changes
        db.session.commit()
        
        print("✅ Database initialized successfully with performance optimizations!")
        print("📊 Created tables with indexes for:")
        print("   - Items (name, item_code, gtin, category, created_at)")
        print("   - Vendors (name, contact_person, email, created_at)")
        print("   - Lots (lot_code, item_id, vendor_id, quantity, unit_type, expiry_date, receiving_date, created_at, status)")
        print("   - AdminUsers (email, first_name, last_name, is_active, is_super_admin, created_at, last_login)")
        print("   - Printers (name, ip_address, printer_type, status, last_seen)")
        print("🚀 Performance features enabled:")
        print("   - Database indexes on frequently queried fields")
        print("   - In-memory caching (5-minute TTL)")
        print("   - Query optimization with joinedload")
        print("   - Connection pooling")
        print("   - Rate limiting")
        print("👤 Default admin user created:")
        print("   Email: admin@inventory.com")
        print("   Password: admin123")

if __name__ == '__main__':
    init_database()


