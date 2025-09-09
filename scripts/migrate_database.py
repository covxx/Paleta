#!/usr/bin/env python3
"""
Database Migration Script for ProduceFlow
This script handles database schema migrations safely without data loss
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

def get_db_path():
    """Get the database path"""
    return current_dir / "instance" / "inventory.db"

def backup_database():
    """Create a backup of the current database"""
    db_path = get_db_path()
    if not db_path.exists():
        print("No existing database found, skipping backup")
        return None
    
    backup_dir = current_dir / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"migration_backup_{timestamp}.db"
    
    shutil.copy2(db_path, backup_path)
    print(f"Database backed up to: {backup_path}")
    return backup_path

def get_schema_version():
    """Get the current schema version"""
    db_path = get_db_path()
    if not db_path.exists():
        return 0
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if schema_version table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='schema_version'
        """)
        
        if not cursor.fetchone():
            conn.close()
            return 0
        
        # Get current version
        cursor.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0
        
    except Exception as e:
        print(f"Error getting schema version: {e}")
        return 0

def set_schema_version(version):
    """Set the schema version"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create schema_version table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version INTEGER NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT
        )
    """)
    
    # Insert new version
    cursor.execute("""
        INSERT INTO schema_version (version, description) 
        VALUES (?, ?)
    """, (version, f"Migration to version {version}"))
    
    conn.commit()
    conn.close()
    print(f"Schema version set to: {version}")

def run_migration(version, description, migration_sql):
    """Run a database migration"""
    print(f"\n=== Migration {version}: {description} ===")
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Run the migration SQL
        if isinstance(migration_sql, list):
            for sql in migration_sql:
                print(f"Executing: {sql[:50]}...")
                cursor.execute(sql)
        else:
            print(f"Executing: {migration_sql[:50]}...")
            cursor.execute(migration_sql)
        
        conn.commit()
        print(f"✓ Migration {version} completed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration {version} failed: {e}")
        raise
    finally:
        conn.close()

def migrate_to_latest():
    """Run all pending migrations"""
    current_version = get_schema_version()
    print(f"Current schema version: {current_version}")
    
    # Define migrations
    migrations = [
        {
            'version': 1,
            'description': 'Add schema_version table',
            'sql': """
                CREATE TABLE IF NOT EXISTS schema_version (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version INTEGER NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            """
        },
        {
            'version': 2,
            'description': 'Add indexes for better performance',
            'sql': [
                "CREATE INDEX IF NOT EXISTS idx_item_name ON item(name)",
                "CREATE INDEX IF NOT EXISTS idx_item_code ON item(item_code)",
                "CREATE INDEX IF NOT EXISTS idx_lot_code ON lot(lot_code)",
                "CREATE INDEX IF NOT EXISTS idx_lot_item_id ON lot(item_id)",
                "CREATE INDEX IF NOT EXISTS idx_vendor_name ON vendor(name)"
            ]
        },
        {
            'version': 3,
            'description': 'Add printer status tracking',
            'sql': """
                ALTER TABLE printer ADD COLUMN last_seen TIMESTAMP;
                ALTER TABLE printer ADD COLUMN status VARCHAR(20) DEFAULT 'offline';
            """
        },
        {
            'version': 4,
            'description': 'Add user session tracking',
            'sql': """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id VARCHAR(100) NOT NULL,
                    session_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        }
    ]
    
    # Run pending migrations
    for migration in migrations:
        if migration['version'] > current_version:
            run_migration(
                migration['version'],
                migration['description'],
                migration['sql']
            )
            set_schema_version(migration['version'])
    
    final_version = get_schema_version()
    print(f"\n✓ Database migration complete. Current version: {final_version}")

def main():
    """Main migration function"""
    print("=== ProduceFlow Database Migration ===")
    
    # Create backup
    backup_path = backup_database()
    
    try:
        # Run migrations
        migrate_to_latest()
        print("\n✓ All migrations completed successfully")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        if backup_path:
            print(f"Database backup available at: {backup_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()
