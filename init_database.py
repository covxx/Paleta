#!/usr/bin/env python3
"""
Database initialization script for QuickBooks Label Printer
This script initializes the database without importing the full app
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def init_database():
    """Initialize the database with all required tables"""
    try:
        # Import Flask and SQLAlchemy
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        
        # Create a minimal Flask app for database initialization
        app = Flask(__name__)
        
        # Set up database configuration
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{current_dir}/instance/inventory.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize SQLAlchemy
        db = SQLAlchemy(app)
        
        # Import all models from the main app
        print("Importing database models...")
        
        # Define all the models here to avoid importing the full app
        class Item(db.Model):
            __tablename__ = 'item'
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(100), nullable=False)
            description = db.Column(db.Text)
            sku = db.Column(db.String(50), unique=True, nullable=False)
            price = db.Column(db.Numeric(10, 2), nullable=False)
            quantity = db.Column(db.Integer, default=0)
            min_quantity = db.Column(db.Integer, default=0)
            vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
            created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
            updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
            quickbooks_id = db.Column(db.String(50), nullable=True)
            
        class Vendor(db.Model):
            __tablename__ = 'vendor'
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(100), nullable=False)
            contact_person = db.Column(db.String(100))
            email = db.Column(db.String(100))
            phone = db.Column(db.String(20))
            address = db.Column(db.Text)
            created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
            updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
            
        class Lot(db.Model):
            __tablename__ = 'lot'
            id = db.Column(db.Integer, primary_key=True)
            lot_number = db.Column(db.String(50), unique=True, nullable=False)
            item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
            quantity = db.Column(db.Integer, nullable=False)
            expiry_date = db.Column(db.Date)
            received_date = db.Column(db.Date, nullable=False)
            vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
            created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
            updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
            
        class Printer(db.Model):
            __tablename__ = 'printer'
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(100), nullable=False)
            ip_address = db.Column(db.String(15), nullable=False)
            port = db.Column(db.Integer, default=9100)
            is_active = db.Column(db.Boolean, default=True)
            created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
            updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
            
        class Customer(db.Model):
            __tablename__ = 'customer'
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(100), nullable=False)
            email = db.Column(db.String(100))
            phone = db.Column(db.String(20))
            address = db.Column(db.Text)
            created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
            updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
            quickbooks_id = db.Column(db.String(50), nullable=True)
            
        class Order(db.Model):
            __tablename__ = 'order'
            id = db.Column(db.Integer, primary_key=True)
            customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
            order_date = db.Column(db.DateTime, default=db.func.current_timestamp())
            status = db.Column(db.String(20), default='pending')
            total_amount = db.Column(db.Numeric(10, 2), default=0)
            notes = db.Column(db.Text)
            created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
            updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
            quickbooks_id = db.Column(db.String(50), nullable=True)
            
        class OrderItem(db.Model):
            __tablename__ = 'order_item'
            id = db.Column(db.Integer, primary_key=True)
            order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
            item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
            quantity = db.Column(db.Integer, nullable=False)
            price = db.Column(db.Numeric(10, 2), nullable=False)
            created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
            
        class SyncLog(db.Model):
            __tablename__ = 'sync_log'
            id = db.Column(db.Integer, primary_key=True)
            sync_type = db.Column(db.String(50), nullable=False, index=True)
            status = db.Column(db.String(20), nullable=False, index=True)
            message = db.Column(db.Text, nullable=False)
            timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), index=True)
            details = db.Column(db.Text, nullable=True)
            records_processed = db.Column(db.Integer, default=0)
            records_successful = db.Column(db.Integer, default=0)
            records_failed = db.Column(db.Integer, default=0)
            notes = db.Column(db.Text, nullable=True)
            created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
            updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
            
        class SyncStatus(db.Model):
            __tablename__ = 'sync_status'
            id = db.Column(db.Integer, primary_key=True)
            sync_type = db.Column(db.String(50), nullable=False, unique=True, index=True)
            last_sync_time = db.Column(db.DateTime, nullable=True)
            next_sync_time = db.Column(db.DateTime, nullable=True)
            sync_interval_minutes = db.Column(db.Integer, default=60)
            is_enabled = db.Column(db.Boolean, default=True)
            last_success = db.Column(db.Boolean, default=False)
            last_error = db.Column(db.Text, nullable=True)
            created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
            updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
        
        # Create the database tables
        print("Creating database tables...")
        with app.app_context():
            db.create_all()
            print("Database tables created successfully!")
            
            # Create some initial data
            print("Creating initial data...")
            
            # Create a default printer if none exists
            if Printer.query.count() == 0:
                default_printer = Printer(
                    name="Default Printer",
                    ip_address="192.168.1.100",
                    port=9100,
                    is_active=True
                )
                db.session.add(default_printer)
                print("Created default printer")
            
            # Create initial sync status records
            sync_types = ['customers', 'items', 'orders', 'pricing']
            for sync_type in sync_types:
                if SyncStatus.query.filter_by(sync_type=sync_type).first() is None:
                    sync_status = SyncStatus(
                        sync_type=sync_type,
                        is_enabled=True,
                        sync_interval_minutes=60
                    )
                    db.session.add(sync_status)
            
            db.session.commit()
            print("Initial data created successfully!")
            
        return True
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    print("Initializing QuickBooks Label Printer database...")
    success = init_database()
    if success:
        print("Database initialization completed successfully!")
        sys.exit(0)
    else:
        print("Database initialization failed!")
        sys.exit(1)
