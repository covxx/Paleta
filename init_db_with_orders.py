#!/usr/bin/env python3
"""
Database initialization script for the Label Printer Inventory System with Order Management
This script creates the database with all models including the new order system.
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from decimal import Decimal

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, AdminUser, Item, Vendor, Lot, Printer, Customer, Order, OrderItem, LotAllocation

def init_database():
    """Initialize the database with all tables and sample data"""
    
    with app.app_context():
        print("🗑️  Dropping existing database...")
        # Remove existing database file
        db_file = 'inventory.db'
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"   Removed {db_file}")
        
        print("🏗️  Creating database tables...")
        db.create_all()
        print("   ✅ All tables created successfully")
        
        # Create default admin user
        print("👤 Creating default admin user...")
        existing_admin = AdminUser.query.filter_by(email='admin@inventory.com').first()
        if not existing_admin:
            admin = AdminUser(
                first_name='Admin',
                last_name='User',
                email='admin@inventory.com',
                password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KzKz2K',  # admin123
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("   ✅ Admin user created (admin@inventory.com / admin123)")
        else:
            print("   ✅ Admin user already exists (admin@inventory.com / admin123)")
        
        # Create sample vendors
        print("🏢 Creating sample vendors...")
        vendor_data = [
            {
                'name': 'Fresh Produce Co.',
                'contact_person': 'John Smith',
                'email': 'john@freshproduce.com',
                'phone': '(555) 123-4567',
                'address': '123 Farm Road, Green Valley, CA 90210 - Primary produce supplier'
            },
            {
                'name': 'Quality Meats Ltd.',
                'contact_person': 'Sarah Johnson',
                'email': 'sarah@qualitymeats.com',
                'phone': '(555) 234-5678',
                'address': '456 Butcher Street, Meat City, CA 90211 - Premium meat supplier'
            },
            {
                'name': 'Dairy Direct',
                'contact_person': 'Mike Wilson',
                'email': 'mike@dairydirect.com',
                'phone': '(555) 345-6789',
                'address': '789 Milk Lane, Dairy Town, CA 90212 - Dairy products supplier'
            }
        ]
        
        vendors_created = 0
        for vendor_info in vendor_data:
            existing_vendor = Vendor.query.filter_by(name=vendor_info['name']).first()
            if not existing_vendor:
                vendor = Vendor(**vendor_info)
                db.session.add(vendor)
                vendors_created += 1
        
        db.session.commit()
        print(f"   ✅ Created {vendors_created} new sample vendors")
        
        # Create sample items
        print("📦 Creating sample items...")
        item_data = [
            {
                'name': 'Organic Tomatoes',
                'item_code': 'TOM-ORG-001',
                'gtin': '1234567890123',
                'category': 'Produce',
                'description': 'Fresh organic tomatoes - High quality organic tomatoes from Fresh Produce Co. Store refrigerated.'
            },
            {
                'name': 'Grass-Fed Beef',
                'item_code': 'BEEF-GF-001',
                'gtin': '2345678901234',
                'category': 'Meat',
                'description': 'Premium grass-fed beef - Premium grass-fed beef cuts from Quality Meats Ltd. Store frozen.'
            },
            {
                'name': 'Organic Milk',
                'item_code': 'MILK-ORG-001',
                'gtin': '3456789012345',
                'category': 'Dairy',
                'description': 'Fresh organic whole milk - Fresh organic whole milk from Dairy Direct. Store refrigerated.'
            },
            {
                'name': 'Free-Range Eggs',
                'item_code': 'EGGS-FR-001',
                'gtin': '4567890123456',
                'category': 'Dairy',
                'description': 'Free-range chicken eggs - Fresh free-range eggs from Dairy Direct. Store refrigerated.'
            }
        ]
        
        items_created = 0
        for item_info in item_data:
            existing_item = Item.query.filter_by(item_code=item_info['item_code']).first()
            if not existing_item:
                item = Item(**item_info)
                db.session.add(item)
                items_created += 1
        
        db.session.commit()
        print(f"   ✅ Created {items_created} new sample items")
        
        # Create sample lots
        print("📋 Creating sample lots...")
        lot_data = [
            {
                'lot_code': 'LOT-TOM-001',
                'item_id': 1,
                'vendor_id': 1,
                'quantity': 100,
                'unit_type': 'lbs',
                'expiry_date': (datetime.now(timezone.utc) + timedelta(days=7)).date(),
                'receiving_date': (datetime.now(timezone.utc) - timedelta(days=1)).date(),
                'notes': 'Fresh delivery from farm',
                'status': 'available'
            },
            {
                'lot_code': 'LOT-BEEF-001',
                'item_id': 2,
                'vendor_id': 2,
                'quantity': 50,
                'unit_type': 'lbs',
                'expiry_date': (datetime.now(timezone.utc) + timedelta(days=30)).date(),
                'receiving_date': (datetime.now(timezone.utc) - timedelta(days=2)).date(),
                'notes': 'Premium grass-fed beef',
                'status': 'available'
            },
            {
                'lot_code': 'LOT-MILK-001',
                'item_id': 3,
                'vendor_id': 3,
                'quantity': 25,
                'unit_type': 'gallons',
                'expiry_date': (datetime.now(timezone.utc) + timedelta(days=14)).date(),
                'receiving_date': (datetime.now(timezone.utc) - timedelta(days=1)).date(),
                'notes': 'Fresh organic milk',
                'status': 'available'
            },
            {
                'lot_code': 'LOT-EGGS-001',
                'item_id': 4,
                'vendor_id': 3,
                'quantity': 20,
                'unit_type': 'dozen',
                'expiry_date': (datetime.now(timezone.utc) + timedelta(days=21)).date(),
                'receiving_date': (datetime.now(timezone.utc) - timedelta(days=1)).date(),
                'notes': 'Fresh free-range eggs',
                'status': 'available'
            }
        ]
        
        lots_created = 0
        for lot_info in lot_data:
            existing_lot = Lot.query.filter_by(lot_code=lot_info['lot_code']).first()
            if not existing_lot:
                lot = Lot(**lot_info)
                db.session.add(lot)
                lots_created += 1
        
        db.session.commit()
        print(f"   ✅ Created {lots_created} new sample lots")
        
        # Create sample customers
        print("👥 Creating sample customers...")
        customer_data = [
            {
                'name': 'Green Restaurant',
                'email': 'orders@greenrestaurant.com',
                'phone': '(555) 111-2222',
                'bill_to_name': 'Green Restaurant',
                'bill_to_address1': '100 Main Street',
                'bill_to_city': 'Downtown',
                'bill_to_state': 'CA',
                'bill_to_zip': '90210',
                'ship_to_name': 'Green Restaurant',
                'ship_to_address1': '100 Main Street',
                'ship_to_city': 'Downtown',
                'ship_to_state': 'CA',
                'ship_to_zip': '90210',
                'payment_terms': 'Net 30',
                'notes': 'Regular customer - organic focus'
            },
            {
                'name': 'Farm Fresh Market',
                'email': 'orders@farmfreshmarket.com',
                'phone': '(555) 333-4444',
                'bill_to_name': 'Farm Fresh Market',
                'bill_to_address1': '200 Market Street',
                'bill_to_city': 'Farm Town',
                'bill_to_state': 'CA',
                'bill_to_zip': '90211',
                'ship_to_name': 'Farm Fresh Market',
                'ship_to_address1': '200 Market Street',
                'ship_to_city': 'Farm Town',
                'ship_to_state': 'CA',
                'ship_to_zip': '90211',
                'payment_terms': 'Net 15',
                'notes': 'Local market - high volume'
            },
            {
                'name': 'Healthy Living Store',
                'email': 'orders@healthyliving.com',
                'phone': '(555) 555-6666',
                'bill_to_name': 'Healthy Living Store',
                'bill_to_address1': '300 Health Avenue',
                'bill_to_city': 'Wellness City',
                'bill_to_state': 'CA',
                'bill_to_zip': '90212',
                'ship_to_name': 'Healthy Living Store',
                'ship_to_address1': '300 Health Avenue',
                'ship_to_city': 'Wellness City',
                'ship_to_state': 'CA',
                'ship_to_zip': '90212',
                'payment_terms': 'Net 30',
                'notes': 'Health food store - premium products'
            }
        ]
        
        customers_created = 0
        for customer_info in customer_data:
            existing_customer = Customer.query.filter_by(name=customer_info['name']).first()
            if not existing_customer:
                customer = Customer(**customer_info)
                db.session.add(customer)
                customers_created += 1
        
        db.session.commit()
        print(f"   ✅ Created {customers_created} new sample customers")
        
        # Create sample orders
        print("📋 Creating sample orders...")
        order_data = [
            {
                'order_number': 'ORD-20241201-001',
                'customer_id': 1,
                'order_date': datetime.now(timezone.utc) - timedelta(days=1),
                'requested_delivery_date': (datetime.now(timezone.utc) + timedelta(days=1)).date(),
                'status': 'pending',
                'subtotal': Decimal('150.00'),
                'tax_amount': Decimal('13.13'),
                'total_amount': Decimal('163.13'),
                'notes': 'Regular weekly order',
                'created_by': 1
            },
            {
                'order_number': 'ORD-20241201-002',
                'customer_id': 2,
                'order_date': datetime.now(timezone.utc) - timedelta(days=2),
                'requested_delivery_date': (datetime.now(timezone.utc) + timedelta(days=2)).date(),
                'status': 'in_progress',
                'subtotal': Decimal('275.00'),
                'tax_amount': Decimal('24.06'),
                'total_amount': Decimal('299.06'),
                'notes': 'Large order for weekend special',
                'created_by': 1
            }
        ]
        
        orders_created = 0
        for order_info in order_data:
            existing_order = Order.query.filter_by(order_number=order_info['order_number']).first()
            if not existing_order:
                order = Order(**order_info)
                db.session.add(order)
                orders_created += 1
        
        db.session.flush()  # Get order IDs
        
        # Create sample order items
        print("📦 Creating sample order items...")
        order_item_data = [
            {
                'order_id': 1,
                'item_id': 1,
                'quantity_ordered': Decimal('30.0'),
                'quantity_filled': Decimal('0.0'),
                'unit_price': Decimal('3.50'),
                'total_price': Decimal('105.00'),
                'status': 'pending',
                'notes': 'Organic tomatoes for salads'
            },
            {
                'order_id': 1,
                'item_id': 4,
                'quantity_ordered': Decimal('5.0'),
                'quantity_filled': Decimal('0.0'),
                'unit_price': Decimal('4.50'),
                'total_price': Decimal('22.50'),
                'status': 'pending',
                'notes': 'Free-range eggs for breakfast'
            },
            {
                'order_id': 1,
                'item_id': 3,
                'quantity_ordered': Decimal('5.0'),
                'quantity_filled': Decimal('0.0'),
                'unit_price': Decimal('5.50'),
                'total_price': Decimal('27.50'),
                'status': 'pending',
                'notes': 'Organic milk for coffee'
            },
            {
                'order_id': 2,
                'item_id': 2,
                'quantity_ordered': Decimal('25.0'),
                'quantity_filled': Decimal('10.0'),
                'unit_price': Decimal('10.99'),
                'total_price': Decimal('274.75'),
                'status': 'partial',
                'notes': 'Grass-fed beef for weekend special'
            }
        ]
        
        order_items_created = 0
        for order_item_info in order_item_data:
            # Check if order item already exists (by order_id and item_id combination)
            existing_order_item = OrderItem.query.filter_by(
                order_id=order_item_info['order_id'],
                item_id=order_item_info['item_id']
            ).first()
            if not existing_order_item:
                order_item = OrderItem(**order_item_info)
                db.session.add(order_item)
                order_items_created += 1
        
        db.session.commit()
        print(f"   ✅ Created {order_items_created} new sample order items")
        
        # Create sample lot allocations
        print("🔗 Creating sample lot allocations...")
        lot_allocation_data = [
            {
                'order_item_id': 4,  # Beef order item
                'lot_id': 2,  # Beef lot
                'quantity_allocated': Decimal('10.0'),
                'allocated_by': 1
            }
        ]
        
        lot_allocations_created = 0
        for allocation_info in lot_allocation_data:
            # Check if lot allocation already exists
            existing_allocation = LotAllocation.query.filter_by(
                order_item_id=allocation_info['order_item_id'],
                lot_id=allocation_info['lot_id']
            ).first()
            if not existing_allocation:
                allocation = LotAllocation(**allocation_info)
                db.session.add(allocation)
                lot_allocations_created += 1
        
        db.session.commit()
        print(f"   ✅ Created {lot_allocations_created} new sample lot allocations")
        
        # Create sample printer
        print("🖨️  Creating sample printer...")
        existing_printer = Printer.query.filter_by(name='Zebra ZD420').first()
        if not existing_printer:
            printer = Printer(
                name='Zebra ZD420',
                ip_address='192.168.1.100',
                port=9100,
                printer_type='zebra',
                label_width=4.0,
                label_height=2.0,
                dpi=203,
                status='offline'
            )
            db.session.add(printer)
            db.session.commit()
            print("   ✅ Sample printer created")
        else:
            print("   ✅ Sample printer already exists")
        
        print("\n🎉 **Database Initialization Complete!**")
        print("\n📊 **Database Summary:**")
        print(f"   👤 Admin Users: 1")
        print(f"   🏢 Vendors: {vendors_created} new")
        print(f"   📦 Items: {items_created} new")
        print(f"   📋 Lots: {lots_created} new")
        print(f"   👥 Customers: {customers_created} new")
        print(f"   📋 Orders: {orders_created} new")
        print(f"   📦 Order Items: {order_items_created} new")
        print(f"   🔗 Lot Allocations: {lot_allocations_created} new")
        print(f"   🖨️  Printers: 1")
        
        print("\n🔑 **Login Credentials:**")
        print("   Email: admin@inventory.com")
        print("   Password: admin123")
        
        print("\n🚀 **Order System Features:**")
        print("   ✅ Customer management with billing/shipping addresses")
        print("   ✅ Order entry with customer selection")
        print("   ✅ Order filling with lot tracking")
        print("   ✅ QuickBooks Online integration ready")
        print("   ✅ Complete lot traceability")
        
        print("\n🌐 **Access URLs:**")
        print("   Main System: http://localhost:5001")
        print("   Orders: http://localhost:5001/orders")
        print("   New Order: http://localhost:5001/orders/new")
        print("   Customers: http://localhost:5001/customers")

if __name__ == '__main__':
    init_database()
