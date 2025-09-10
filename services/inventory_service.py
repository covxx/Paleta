"""
Inventory Service

Handles all business logic related to inventory management including
items, lots, vendors, and stock level operations.
"""

from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.exc import IntegrityError
from app import db
from models import Item, Lot, Vendor


class InventoryService:
    """Service class for inventory management operations"""
    
    @staticmethod
    def get_all_items() -> List[Dict]:
        """Get all items with their details"""
        try:
            items = Item.query.order_by(Item.name.asc()).all()
            return [
                {
                    'id': item.id,
                    'name': item.name,
                    'item_code': item.item_code,
                    'gtin': item.gtin,
                    'category': item.category,
                    'description': item.description,
                    'unit_price': float(item.unit_price) if item.unit_price else 0.0,
                    'quickbooks_id': item.quickbooks_id,
                    'created_at': item.created_at.isoformat() if item.created_at else None,
                    'updated_at': item.updated_at.isoformat() if item.updated_at else None,
                    'total_lots': len(item.lots),
                    'total_quantity': sum(lot.quantity for lot in item.lots if lot.status == 'active')
                }
                for item in items
            ]
        except Exception as e:
            raise Exception(f"Failed to retrieve items: {str(e)}")
    
    @staticmethod
    def get_item_by_id(item_id: int) -> Optional[Dict]:
        """Get a specific item by ID"""
        try:
            item = Item.query.get(item_id)
            if not item:
                return None
            
            return {
                'id': item.id,
                'name': item.name,
                'item_code': item.item_code,
                'gtin': item.gtin,
                'category': item.category,
                'description': item.description,
                'unit_price': float(item.unit_price) if item.unit_price else 0.0,
                'quickbooks_id': item.quickbooks_id,
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'updated_at': item.updated_at.isoformat() if item.updated_at else None,
                'lots': [
                    {
                        'id': lot.id,
                        'lot_code': lot.lot_code,
                        'quantity': lot.quantity,
                        'unit': lot.unit,
                        'expiry_date': lot.expiry_date.isoformat() if lot.expiry_date else None,
                        'status': lot.status,
                        'created_at': lot.created_at.isoformat() if lot.created_at else None
                    }
                    for lot in item.lots
                ]
            }
        except Exception as e:
            raise Exception(f"Failed to retrieve item {item_id}: {str(e)}")
    
    @staticmethod
    def create_item(item_data: Dict) -> Dict:
        """Create a new item"""
        try:
            # Validate required fields
            if not item_data.get('name'):
                raise ValueError("Item name is required")
            
            # Check for duplicate item code
            if item_data.get('item_code'):
                existing_item = Item.query.filter_by(item_code=item_data['item_code']).first()
                if existing_item:
                    raise ValueError(f"Item code '{item_data['item_code']}' already exists")
            
            # Create new item
            item = Item(
                name=item_data['name'],
                item_code=item_data.get('item_code'),
                gtin=item_data.get('gtin'),
                category=item_data.get('category'),
                description=item_data.get('description'),
                unit_price=item_data.get('unit_price', 0.0),
                quickbooks_id=item_data.get('quickbooks_id')
            )
            
            db.session.add(item)
            db.session.commit()
            
            return {
                'id': item.id,
                'name': item.name,
                'item_code': item.item_code,
                'message': 'Item created successfully'
            }
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Database integrity error: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create item: {str(e)}")
    
    @staticmethod
    def update_item(item_id: int, item_data: Dict) -> Dict:
        """Update an existing item"""
        try:
            item = Item.query.get(item_id)
            if not item:
                raise ValueError(f"Item with ID {item_id} not found")
            
            # Check for duplicate item code (excluding current item)
            if item_data.get('item_code') and item_data['item_code'] != item.item_code:
                existing_item = Item.query.filter(
                    and_(Item.item_code == item_data['item_code'], Item.id != item_id)
                ).first()
                if existing_item:
                    raise ValueError(f"Item code '{item_data['item_code']}' already exists")
            
            # Update fields
            if 'name' in item_data:
                item.name = item_data['name']
            if 'item_code' in item_data:
                item.item_code = item_data['item_code']
            if 'gtin' in item_data:
                item.gtin = item_data['gtin']
            if 'category' in item_data:
                item.category = item_data['category']
            if 'description' in item_data:
                item.description = item_data['description']
            if 'unit_price' in item_data:
                item.unit_price = item_data['unit_price']
            if 'quickbooks_id' in item_data:
                item.quickbooks_id = item_data['quickbooks_id']
            
            item.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'id': item.id,
                'name': item.name,
                'message': 'Item updated successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update item: {str(e)}")
    
    @staticmethod
    def delete_item(item_id: int) -> Dict:
        """Delete an item (soft delete by checking for active lots)"""
        try:
            item = Item.query.get(item_id)
            if not item:
                raise ValueError(f"Item with ID {item_id} not found")
            
            # Check if item has active lots
            active_lots = Lot.query.filter(
                and_(Lot.item_id == item_id, Lot.status == 'active')
            ).count()
            
            if active_lots > 0:
                raise ValueError(f"Cannot delete item with {active_lots} active lots")
            
            db.session.delete(item)
            db.session.commit()
            
            return {
                'id': item_id,
                'message': 'Item deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete item: {str(e)}")
    
    @staticmethod
    def get_all_lots() -> List[Dict]:
        """Get all lots with item and vendor information"""
        try:
            lots = db.session.query(Lot, Item, Vendor).outerjoin(
                Item, Lot.item_id == Item.id
            ).outerjoin(
                Vendor, Lot.vendor_id == Vendor.id
            ).order_by(desc(Lot.created_at)).all()
            
            return [
                {
                    'id': lot.id,
                    'lot_code': lot.lot_code,
                    'item_id': lot.item_id,
                    'item_name': item.name if item else 'Unknown Item',
                    'quantity': lot.quantity,
                    'unit': lot.unit,
                    'expiry_date': lot.expiry_date.isoformat() if lot.expiry_date else None,
                    'vendor_id': lot.vendor_id,
                    'vendor_name': vendor.name if vendor else 'Unknown Vendor',
                    'status': lot.status,
                    'created_at': lot.created_at.isoformat() if lot.created_at else None,
                    'days_until_expiry': (lot.expiry_date - date.today()).days if lot.expiry_date else None
                }
                for lot, item, vendor in lots
            ]
        except Exception as e:
            raise Exception(f"Failed to retrieve lots: {str(e)}")
    
    @staticmethod
    def get_lot_by_id(lot_id: int) -> Optional[Dict]:
        """Get a specific lot by ID"""
        try:
            lot = Lot.query.get(lot_id)
            if not lot:
                return None
            
            item = Item.query.get(lot.item_id)
            vendor = Vendor.query.get(lot.vendor_id) if lot.vendor_id else None
            
            return {
                'id': lot.id,
                'lot_code': lot.lot_code,
                'item_id': lot.item_id,
                'item_name': item.name if item else 'Unknown Item',
                'quantity': lot.quantity,
                'unit': lot.unit,
                'expiry_date': lot.expiry_date.isoformat() if lot.expiry_date else None,
                'vendor_id': lot.vendor_id,
                'vendor_name': vendor.name if vendor else 'Unknown Vendor',
                'status': lot.status,
                'created_at': lot.created_at.isoformat() if lot.created_at else None,
                'days_until_expiry': (lot.expiry_date - date.today()).days if lot.expiry_date else None
            }
        except Exception as e:
            raise Exception(f"Failed to retrieve lot {lot_id}: {str(e)}")
    
    @staticmethod
    def create_lot(lot_data: Dict) -> Dict:
        """Create a new lot"""
        try:
            # Validate required fields
            if not lot_data.get('lot_code'):
                raise ValueError("LOT code is required")
            if not lot_data.get('item_id'):
                raise ValueError("Item ID is required")
            if not lot_data.get('quantity'):
                raise ValueError("Quantity is required")
            
            # Check for duplicate lot code
            existing_lot = Lot.query.filter_by(lot_code=lot_data['lot_code']).first()
            if existing_lot:
                raise ValueError(f"LOT code '{lot_data['lot_code']}' already exists")
            
            # Verify item exists
            item = Item.query.get(lot_data['item_id'])
            if not item:
                raise ValueError(f"Item with ID {lot_data['item_id']} not found")
            
            # Create new lot
            lot = Lot(
                lot_code=lot_data['lot_code'],
                item_id=lot_data['item_id'],
                quantity=lot_data['quantity'],
                unit=lot_data.get('unit', 'pcs'),
                expiry_date=datetime.strptime(lot_data['expiry_date'], '%Y-%m-%d').date() if lot_data.get('expiry_date') else None,
                vendor_id=lot_data.get('vendor_id'),
                status=lot_data.get('status', 'active')
            )
            
            db.session.add(lot)
            db.session.commit()
            
            return {
                'id': lot.id,
                'lot_code': lot.lot_code,
                'item_name': item.name,
                'message': 'LOT created successfully'
            }
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Database integrity error: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create lot: {str(e)}")
    
    @staticmethod
    def update_lot(lot_id: int, lot_data: Dict) -> Dict:
        """Update an existing lot"""
        try:
            lot = Lot.query.get(lot_id)
            if not lot:
                raise ValueError(f"LOT with ID {lot_id} not found")
            
            # Check for duplicate lot code (excluding current lot)
            if lot_data.get('lot_code') and lot_data['lot_code'] != lot.lot_code:
                existing_lot = Lot.query.filter(
                    and_(Lot.lot_code == lot_data['lot_code'], Lot.id != lot_id)
                ).first()
                if existing_lot:
                    raise ValueError(f"LOT code '{lot_data['lot_code']}' already exists")
            
            # Update fields
            if 'lot_code' in lot_data:
                lot.lot_code = lot_data['lot_code']
            if 'quantity' in lot_data:
                lot.quantity = lot_data['quantity']
            if 'unit' in lot_data:
                lot.unit = lot_data['unit']
            if 'expiry_date' in lot_data:
                lot.expiry_date = datetime.strptime(lot_data['expiry_date'], '%Y-%m-%d').date() if lot_data['expiry_date'] else None
            if 'vendor_id' in lot_data:
                lot.vendor_id = lot_data['vendor_id']
            if 'status' in lot_data:
                lot.status = lot_data['status']
            
            db.session.commit()
            
            return {
                'id': lot.id,
                'lot_code': lot.lot_code,
                'message': 'LOT updated successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update lot: {str(e)}")
    
    @staticmethod
    def delete_lot(lot_id: int) -> Dict:
        """Delete a lot"""
        try:
            lot = Lot.query.get(lot_id)
            if not lot:
                raise ValueError(f"LOT with ID {lot_id} not found")
            
            db.session.delete(lot)
            db.session.commit()
            
            return {
                'id': lot_id,
                'message': 'LOT deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete lot: {str(e)}")
    
    @staticmethod
    def get_expiring_lots(days: int = 7) -> List[Dict]:
        """Get lots expiring within specified days"""
        try:
            expiry_date = date.today() + datetime.timedelta(days=days)
            lots = db.session.query(Lot, Item, Vendor).outerjoin(
                Item, Lot.item_id == Item.id
            ).outerjoin(
                Vendor, Lot.vendor_id == Vendor.id
            ).filter(
                and_(
                    Lot.expiry_date <= expiry_date,
                    Lot.expiry_date >= date.today(),
                    Lot.status == 'active'
                )
            ).order_by(Lot.expiry_date.asc()).all()
            
            return [
                {
                    'id': lot.id,
                    'lot_code': lot.lot_code,
                    'item_name': item.name if item else 'Unknown Item',
                    'quantity': lot.quantity,
                    'unit': lot.unit,
                    'expiry_date': lot.expiry_date.isoformat(),
                    'vendor_name': vendor.name if vendor else 'Unknown Vendor',
                    'days_until_expiry': (lot.expiry_date - date.today()).days
                }
                for lot, item, vendor in lots
            ]
        except Exception as e:
            raise Exception(f"Failed to retrieve expiring lots: {str(e)}")
    
    @staticmethod
    def get_inventory_statistics() -> Dict:
        """Get inventory statistics"""
        try:
            total_items = Item.query.count()
            total_lots = Lot.query.count()
            active_lots = Lot.query.filter_by(status='active').count()
            total_vendors = Vendor.query.count()
            
            # Calculate total inventory value
            total_value = db.session.query(
                db.func.sum(Lot.quantity * Item.unit_price)
            ).join(Item, Lot.item_id == Item.id).filter(
                Lot.status == 'active'
            ).scalar() or 0.0
            
            # Get expiring lots count
            expiry_date = date.today() + datetime.timedelta(days=7)
            expiring_lots = Lot.query.filter(
                and_(
                    Lot.expiry_date <= expiry_date,
                    Lot.expiry_date >= date.today(),
                    Lot.status == 'active'
                )
            ).count()
            
            return {
                'total_items': total_items,
                'total_lots': total_lots,
                'active_lots': active_lots,
                'total_vendors': total_vendors,
                'total_inventory_value': float(total_value),
                'expiring_lots_7_days': expiring_lots
            }
        except Exception as e:
            raise Exception(f"Failed to retrieve inventory statistics: {str(e)}")
