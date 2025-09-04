#!/usr/bin/env python3
"""
Initialize database with unit_type support
"""

from app import app, db, Item, Lot, Vendor, Printer, AdminUser, PrintJob
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone, timedelta

def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Add sample vendors
        vendors = [
            Vendor(
                name="Quality Foods Inc.",
                contact_person="John Smith",
                email="john@qualityfoods.com",
                phone="555-0101",
                address="123 Food Street, City, State 12345"
            ),
            Vendor(
                name="Fresh Produce Co.",
                contact_person="Sarah Johnson",
                email="sarah@freshproduce.com",
                phone="555-0102",
                address="456 Farm Road, City, State 12345"
            ),
            Vendor(
                name="Premium Suppliers LLC",
                contact_person="Mike Davis",
                email="mike@premiumsuppliers.com",
                phone="555-0103",
                address="789 Warehouse Blvd, City, State 12345"
            )
        ]
        
        for vendor in vendors:
            db.session.add(vendor)
        
        # Add sample items
        items = [
            Item(
                name="Premium Coffee Beans",
                description="High-quality arabica coffee beans",
                item_code="COFFEE001",
                gtin="1234567890123",
                category="Beverages"
            ),
            Item(
                name="Organic Green Tea",
                description="Premium organic green tea leaves",
                item_code="TEA002",
                gtin="1234567890124",
                category="Beverages"
            ),
            Item(
                name="Raw Honey",
                description="Pure raw honey from local beekeepers",
                item_code="HONEY003",
                gtin="1234567890125",
                category="Sweeteners"
            ),
            Item(
                name="Whole Wheat Flour",
                description="Organic whole wheat flour",
                item_code="FLOUR004",
                gtin="1234567890126",
                category="Baking"
            ),
            Item(
                name="Extra Virgin Olive Oil",
                description="Cold-pressed extra virgin olive oil",
                item_code="OIL005",
                gtin="1234567890127",
                category="Cooking"
            )
        ]
        
        for item in items:
            db.session.add(item)
        
        # Add sample lots with unit types
        lots = [
            Lot(
                lot_code="LOT0001202509040949B2AA",
                item_id=1,
                vendor_id=1,
                quantity=50,
                unit_type="cases",
                receiving_date=datetime.now(timezone.utc).date(),
                expiry_date=(datetime.now(timezone.utc) + timedelta(days=10)).date(),
                notes="Fresh coffee beans from supplier",
                status="active"
            ),
            Lot(
                lot_code="LOT0002202509040950C3BB",
                item_id=2,
                vendor_id=2,
                quantity=25,
                unit_type="pounds",
                receiving_date=datetime.now(timezone.utc).date(),
                expiry_date=(datetime.now(timezone.utc) + timedelta(days=10)).date(),
                notes="Organic green tea leaves",
                status="active"
            ),
            Lot(
                lot_code="LOT0003202509040951D4CC",
                item_id=3,
                vendor_id=1,
                quantity=100,
                unit_type="pounds",
                receiving_date=datetime.now(timezone.utc).date(),
                expiry_date=(datetime.now(timezone.utc) + timedelta(days=10)).date(),
                notes="Raw honey from local beekeepers",
                status="active"
            )
        ]
        
        for lot in lots:
            db.session.add(lot)
        
        # Add sample printer
        printer = Printer(
            name="CJ Test",
            ip_address="192.168.1.100",
            port=9100,
            printer_type="zebra",
            label_width=4.0,
            label_height=2.0,
            dpi=203,
            status="offline"
        )
        db.session.add(printer)
        
        # Add super admin user
        admin = AdminUser(
            email="admin@company.com",
            password_hash=generate_password_hash("admin123"),
            first_name="System",
            last_name="Administrator",
            is_super_admin=True,
            is_active=True
        )
        db.session.add(admin)
        
        # Commit all changes
        db.session.commit()
        print("Database initialized successfully with unit_type support!")
        print(f"Created {len(vendors)} vendors, {len(items)} items, {len(lots)} lots, 1 printer, and 1 admin user")
        print("\nSuper Admin Login Credentials:")
        print("Email: admin@company.com")
        print("Password: admin123")
        print("\nIMPORTANT: Change the default password after first login!")
        print("This user has super admin privileges and can manage other admin users.")

if __name__ == "__main__":
    init_database()
