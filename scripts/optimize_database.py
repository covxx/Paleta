"""
Database Optimization Script

Adds missing indexes and optimizes database performance for better query execution.
"""

import sqlite3
import os
from datetime import datetime


def get_db_path():
    """Get the database file path"""
    return os.path.join('instance', 'inventory.db')


def add_indexes():
    """Add missing database indexes for better performance"""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Adding database indexes for better performance...")
        
        # Item table indexes
        indexes_to_add = [
            # Item table indexes
            ("idx_item_name", "CREATE INDEX IF NOT EXISTS idx_item_name ON item(name)"),
            ("idx_item_code", "CREATE INDEX IF NOT EXISTS idx_item_code ON item(item_code)"),
            ("idx_item_gtin", "CREATE INDEX IF NOT EXISTS idx_item_gtin ON item(gtin)"),
            ("idx_item_category", "CREATE INDEX IF NOT EXISTS idx_item_category ON item(category)"),
            ("idx_item_quickbooks_id", "CREATE INDEX IF NOT EXISTS idx_item_quickbooks_id ON item(quickbooks_id)"),
            ("idx_item_created_at", "CREATE INDEX IF NOT EXISTS idx_item_created_at ON item(created_at)"),
            
            # Lot table indexes
            ("idx_lot_code", "CREATE INDEX IF NOT EXISTS idx_lot_code ON lot(lot_code)"),
            ("idx_lot_item_id", "CREATE INDEX IF NOT EXISTS idx_lot_item_id ON lot(item_id)"),
            ("idx_lot_vendor_id", "CREATE INDEX IF NOT EXISTS idx_lot_vendor_id ON lot(vendor_id)"),
            ("idx_lot_status", "CREATE INDEX IF NOT EXISTS idx_lot_status ON lot(status)"),
            ("idx_lot_expiry_date", "CREATE INDEX IF NOT EXISTS idx_lot_expiry_date ON lot(expiry_date)"),
            ("idx_lot_created_at", "CREATE INDEX IF NOT EXISTS idx_lot_created_at ON lot(created_at)"),
            
            # Order table indexes
            ("idx_order_number", "CREATE INDEX IF NOT EXISTS idx_order_number ON `order`(order_number)"),
            ("idx_order_customer_id", "CREATE INDEX IF NOT EXISTS idx_order_customer_id ON `order`(customer_id)"),
            ("idx_order_status", "CREATE INDEX IF NOT EXISTS idx_order_status ON `order`(status)"),
            ("idx_order_created_at", "CREATE INDEX IF NOT EXISTS idx_order_created_at ON `order`(created_at)"),
            ("idx_order_quickbooks_synced", "CREATE INDEX IF NOT EXISTS idx_order_quickbooks_synced ON `order`(quickbooks_synced)"),
            
            # Customer table indexes
            ("idx_customer_name", "CREATE INDEX IF NOT EXISTS idx_customer_name ON customer(name)"),
            ("idx_customer_email", "CREATE INDEX IF NOT EXISTS idx_customer_email ON customer(email)"),
            ("idx_customer_phone", "CREATE INDEX IF NOT EXISTS idx_customer_phone ON customer(phone)"),
            ("idx_customer_quickbooks_id", "CREATE INDEX IF NOT EXISTS idx_customer_quickbooks_id ON customer(quickbooks_id)"),
            ("idx_customer_created_at", "CREATE INDEX IF NOT EXISTS idx_customer_created_at ON customer(created_at)"),
            
            # Printer table indexes
            ("idx_printer_name", "CREATE INDEX IF NOT EXISTS idx_printer_name ON printer(name)"),
            ("idx_printer_ip_address", "CREATE INDEX IF NOT EXISTS idx_printer_ip_address ON printer(ip_address)"),
            ("idx_printer_status", "CREATE INDEX IF NOT EXISTS idx_printer_status ON printer(status)"),
            ("idx_printer_type", "CREATE INDEX IF NOT EXISTS idx_printer_type ON printer(printer_type)"),
            ("idx_printer_last_seen", "CREATE INDEX IF NOT EXISTS idx_printer_last_seen ON printer(last_seen)"),
            
            # Vendor table indexes
            ("idx_vendor_name", "CREATE INDEX IF NOT EXISTS idx_vendor_name ON vendor(name)"),
            ("idx_vendor_email", "CREATE INDEX IF NOT EXISTS idx_vendor_email ON vendor(email)"),
            ("idx_vendor_created_at", "CREATE INDEX IF NOT EXISTS idx_vendor_created_at ON vendor(created_at)"),
            
            # Admin user table indexes
            ("idx_admin_user_email", "CREATE INDEX IF NOT EXISTS idx_admin_user_email ON admin_user(email)"),
            ("idx_admin_user_last_login", "CREATE INDEX IF NOT EXISTS idx_admin_user_last_login ON admin_user(last_login)"),
            
            # Sync log table indexes
            ("idx_sync_log_type", "CREATE INDEX IF NOT EXISTS idx_sync_log_type ON sync_log(sync_type)"),
            ("idx_sync_log_status", "CREATE INDEX IF NOT EXISTS idx_sync_log_status ON sync_log(status)"),
            ("idx_sync_log_timestamp", "CREATE INDEX IF NOT EXISTS idx_sync_log_timestamp ON sync_log(timestamp)"),
            
            # Composite indexes for common queries
            ("idx_lot_item_status", "CREATE INDEX IF NOT EXISTS idx_lot_item_status ON lot(item_id, status)"),
            ("idx_lot_expiry_status", "CREATE INDEX IF NOT EXISTS idx_lot_expiry_status ON lot(expiry_date, status)"),
            ("idx_order_customer_status", "CREATE INDEX IF NOT EXISTS idx_order_customer_status ON `order`(customer_id, status)"),
            ("idx_order_created_status", "CREATE INDEX IF NOT EXISTS idx_order_created_status ON `order`(created_at, status)"),
        ]
        
        added_count = 0
        for index_name, index_sql in indexes_to_add:
            try:
                cursor.execute(index_sql)
                print(f"✓ Added index: {index_name}")
                added_count += 1
            except sqlite3.Error as e:
                print(f"✗ Failed to add index {index_name}: {e}")
        
        # Analyze the database to update statistics
        print("\nAnalyzing database to update statistics...")
        cursor.execute("ANALYZE")
        
        conn.commit()
        print(f"\n✓ Successfully added {added_count} indexes")
        print("✓ Database analysis completed")
        
        return True
        
    except Exception as e:
        print(f"✗ Error adding indexes: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def check_database_integrity():
    """Check database integrity"""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Checking database integrity...")
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        
        if result[0] == 'ok':
            print("✓ Database integrity check passed")
            return True
        else:
            print(f"✗ Database integrity check failed: {result[0]}")
            return False
            
    except Exception as e:
        print(f"✗ Error checking database integrity: {e}")
        return False
    finally:
        conn.close()


def get_database_info():
    """Get database information and statistics"""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Database Information:")
        print("=" * 50)
        
        # Get database file size
        file_size = os.path.getsize(db_path)
        print(f"Database file size: {file_size / 1024 / 1024:.2f} MB")
        
        # Get table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\nTables ({len(tables)}):")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} rows")
        
        # Get index information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
        indexes = cursor.fetchall()
        
        print(f"\nIndexes ({len(indexes)}):")
        for index in indexes:
            print(f"  - {index[0]}")
        
        # Get database statistics
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        
        print(f"\nDatabase Statistics:")
        print(f"  - Page count: {page_count}")
        print(f"  - Page size: {page_size} bytes")
        print(f"  - Total size: {page_count * page_size / 1024 / 1024:.2f} MB")
        
    except Exception as e:
        print(f"✗ Error getting database info: {e}")
    finally:
        conn.close()


def optimize_database():
    """Main function to optimize the database"""
    print("Database Optimization Script")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check database integrity first
    if not check_database_integrity():
        print("✗ Database integrity check failed. Aborting optimization.")
        return False
    
    # Add indexes
    if not add_indexes():
        print("✗ Failed to add indexes. Aborting optimization.")
        return False
    
    # Get database information
    print("\n" + "=" * 50)
    get_database_info()
    
    print("\n✓ Database optimization completed successfully!")
    return True


if __name__ == "__main__":
    optimize_database()
