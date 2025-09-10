"""
Printer Service

Handles all business logic related to printer management including
printer configuration, connection testing, and label printing.
"""

import socket
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.exc import IntegrityError
from app import db
from models import Printer


class PrinterService:
    """Service class for printer management operations"""
    
    @staticmethod
    def get_all_printers() -> List[Dict]:
        """Get all printers with status information"""
        try:
            printers = Printer.query.order_by(Printer.name.asc()).all()
            
            result = []
            for printer in printers:
                # Check if printer is online (last seen within 5 minutes)
                is_online = False
                if printer.last_seen:
                    time_diff = datetime.utcnow() - printer.last_seen
                    is_online = time_diff.total_seconds() < 300  # 5 minutes
                
                result.append({
                    'id': printer.id,
                    'name': printer.name,
                    'ip_address': printer.ip_address,
                    'port': printer.port,
                    'printer_type': printer.printer_type,
                    'label_width': float(printer.label_width) if printer.label_width else 4.0,
                    'label_height': float(printer.label_height) if printer.label_height else 2.0,
                    'dpi': printer.dpi,
                    'status': 'online' if is_online else 'offline',
                    'last_seen': printer.last_seen.isoformat() if printer.last_seen else None,
                    'created_at': printer.created_at.isoformat() if printer.created_at else None
                })
            
            return result
        except Exception as e:
            raise Exception(f"Failed to retrieve printers: {str(e)}")
    
    @staticmethod
    def get_printer_by_id(printer_id: int) -> Optional[Dict]:
        """Get a specific printer by ID"""
        try:
            printer = Printer.query.get(printer_id)
            if not printer:
                return None
            
            # Check if printer is online
            is_online = False
            if printer.last_seen:
                time_diff = datetime.utcnow() - printer.last_seen
                is_online = time_diff.total_seconds() < 300  # 5 minutes
            
            return {
                'id': printer.id,
                'name': printer.name,
                'ip_address': printer.ip_address,
                'port': printer.port,
                'printer_type': printer.printer_type,
                'label_width': float(printer.label_width) if printer.label_width else 4.0,
                'label_height': float(printer.label_height) if printer.label_height else 2.0,
                'dpi': printer.dpi,
                'status': 'online' if is_online else 'offline',
                'last_seen': printer.last_seen.isoformat() if printer.last_seen else None,
                'created_at': printer.created_at.isoformat() if printer.created_at else None
            }
        except Exception as e:
            raise Exception(f"Failed to retrieve printer {printer_id}: {str(e)}")
    
    @staticmethod
    def create_printer(printer_data: Dict) -> Dict:
        """Create a new printer"""
        try:
            # Validate required fields
            if not printer_data.get('name'):
                raise ValueError("Printer name is required")
            if not printer_data.get('ip_address'):
                raise ValueError("IP address is required")
            
            # Validate IP address format
            try:
                socket.inet_aton(printer_data['ip_address'])
            except socket.error:
                raise ValueError("Invalid IP address format")
            
            # Check for duplicate IP address
            existing_printer = Printer.query.filter_by(ip_address=printer_data['ip_address']).first()
            if existing_printer:
                raise ValueError(f"Printer with IP address '{printer_data['ip_address']}' already exists")
            
            # Create new printer
            printer = Printer(
                name=printer_data['name'],
                ip_address=printer_data['ip_address'],
                port=printer_data.get('port', 9100),
                printer_type=printer_data.get('printer_type', 'zebra'),
                label_width=printer_data.get('label_width', 4.0),
                label_height=printer_data.get('label_height', 2.0),
                dpi=printer_data.get('dpi', 203),
                status='offline'
            )
            
            db.session.add(printer)
            db.session.commit()
            
            return {
                'id': printer.id,
                'name': printer.name,
                'ip_address': printer.ip_address,
                'message': 'Printer created successfully'
            }
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Database integrity error: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create printer: {str(e)}")
    
    @staticmethod
    def update_printer(printer_id: int, printer_data: Dict) -> Dict:
        """Update an existing printer"""
        try:
            printer = Printer.query.get(printer_id)
            if not printer:
                raise ValueError(f"Printer with ID {printer_id} not found")
            
            # Check for duplicate IP address (excluding current printer)
            if printer_data.get('ip_address') and printer_data['ip_address'] != printer.ip_address:
                existing_printer = Printer.query.filter(
                    and_(Printer.ip_address == printer_data['ip_address'], Printer.id != printer_id)
                ).first()
                if existing_printer:
                    raise ValueError(f"Printer with IP address '{printer_data['ip_address']}' already exists")
                
                # Validate IP address format
                try:
                    socket.inet_aton(printer_data['ip_address'])
                except socket.error:
                    raise ValueError("Invalid IP address format")
            
            # Update fields
            if 'name' in printer_data:
                printer.name = printer_data['name']
            if 'ip_address' in printer_data:
                printer.ip_address = printer_data['ip_address']
            if 'port' in printer_data:
                printer.port = printer_data['port']
            if 'printer_type' in printer_data:
                printer.printer_type = printer_data['printer_type']
            if 'label_width' in printer_data:
                printer.label_width = printer_data['label_width']
            if 'label_height' in printer_data:
                printer.label_height = printer_data['label_height']
            if 'dpi' in printer_data:
                printer.dpi = printer_data['dpi']
            
            db.session.commit()
            
            return {
                'id': printer.id,
                'name': printer.name,
                'ip_address': printer.ip_address,
                'message': 'Printer updated successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update printer: {str(e)}")
    
    @staticmethod
    def delete_printer(printer_id: int) -> Dict:
        """Delete a printer"""
        try:
            printer = Printer.query.get(printer_id)
            if not printer:
                raise ValueError(f"Printer with ID {printer_id} not found")
            
            db.session.delete(printer)
            db.session.commit()
            
            return {
                'id': printer_id,
                'message': 'Printer deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete printer: {str(e)}")
    
    @staticmethod
    def test_printer_connection(printer_id: int) -> Dict:
        """Test connection to a printer"""
        try:
            printer = Printer.query.get(printer_id)
            if not printer:
                raise ValueError(f"Printer with ID {printer_id} not found")
            
            # Test network connectivity
            start_time = time.time()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)  # 5 second timeout
                result = sock.connect_ex((printer.ip_address, printer.port))
                sock.close()
                connection_time = time.time() - start_time
                
                if result == 0:
                    # Connection successful, update last_seen
                    printer.last_seen = datetime.utcnow()
                    printer.status = 'online'
                    db.session.commit()
                    
                    return {
                        'id': printer_id,
                        'name': printer.name,
                        'ip_address': printer.ip_address,
                        'port': printer.port,
                        'status': 'online',
                        'connection_time': round(connection_time, 3),
                        'message': 'Connection successful'
                    }
                else:
                    # Connection failed
                    printer.status = 'offline'
                    db.session.commit()
                    
                    return {
                        'id': printer_id,
                        'name': printer.name,
                        'ip_address': printer.ip_address,
                        'port': printer.port,
                        'status': 'offline',
                        'connection_time': round(connection_time, 3),
                        'message': 'Connection failed'
                    }
                    
            except socket.timeout:
                printer.status = 'offline'
                db.session.commit()
                
                return {
                    'id': printer_id,
                    'name': printer.name,
                    'ip_address': printer.ip_address,
                    'port': printer.port,
                    'status': 'offline',
                    'connection_time': 5.0,
                    'message': 'Connection timeout'
                }
            except Exception as e:
                printer.status = 'offline'
                db.session.commit()
                
                return {
                    'id': printer_id,
                    'name': printer.name,
                    'ip_address': printer.ip_address,
                    'port': printer.port,
                    'status': 'offline',
                    'connection_time': 0.0,
                    'message': f'Connection error: {str(e)}'
                }
                
        except Exception as e:
            raise Exception(f"Failed to test printer connection: {str(e)}")
    
    @staticmethod
    def print_label(printer_id: int, label_data: Dict) -> Dict:
        """Print a label to a specific printer"""
        try:
            printer = Printer.query.get(printer_id)
            if not printer:
                raise ValueError(f"Printer with ID {printer_id} not found")
            
            # Generate ZPL code
            zpl_code = PrinterService._generate_zpl_code(label_data, printer)
            
            # Send to printer
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)  # 10 second timeout
                sock.connect((printer.ip_address, printer.port))
                sock.send(zpl_code.encode('utf-8'))
                sock.close()
                
                # Update printer status
                printer.last_seen = datetime.utcnow()
                printer.status = 'online'
                db.session.commit()
                
                return {
                    'id': printer_id,
                    'name': printer.name,
                    'status': 'success',
                    'message': 'Label printed successfully'
                }
                
            except Exception as e:
                printer.status = 'offline'
                db.session.commit()
                
                return {
                    'id': printer_id,
                    'name': printer.name,
                    'status': 'error',
                    'message': f'Print failed: {str(e)}'
                }
                
        except Exception as e:
            raise Exception(f"Failed to print label: {str(e)}")
    
    @staticmethod
    def get_printer_statistics() -> Dict:
        """Get printer statistics"""
        try:
            total_printers = Printer.query.count()
            online_printers = 0
            offline_printers = 0
            
            printers = Printer.query.all()
            for printer in printers:
                if printer.last_seen:
                    time_diff = datetime.utcnow() - printer.last_seen
                    if time_diff.total_seconds() < 300:  # 5 minutes
                        online_printers += 1
                    else:
                        offline_printers += 1
                else:
                    offline_printers += 1
            
            # Get printer types distribution
            printer_types = db.session.query(
                Printer.printer_type,
                db.func.count(Printer.id).label('count')
            ).group_by(Printer.printer_type).all()
            
            return {
                'total_printers': total_printers,
                'online_printers': online_printers,
                'offline_printers': offline_printers,
                'printer_types': [
                    {
                        'type': printer_type,
                        'count': count
                    }
                    for printer_type, count in printer_types
                ]
            }
        except Exception as e:
            raise Exception(f"Failed to retrieve printer statistics: {str(e)}")
    
    @staticmethod
    def _generate_zpl_code(label_data: Dict, printer: Printer) -> str:
        """Generate ZPL code for label printing"""
        try:
            # Extract label data
            item_name = label_data.get('item_name', 'Unknown Item')
            lot_code = label_data.get('lot_code', 'N/A')
            expiry_date = label_data.get('expiry_date', 'N/A')
            quantity = label_data.get('quantity', 'N/A')
            unit = label_data.get('unit', 'pcs')
            
            # Calculate label dimensions in dots
            width_dots = int(printer.label_width * printer.dpi)
            height_dots = int(printer.label_height * printer.dpi)
            
            # Generate ZPL code
            zpl = f"""
^XA
^FO50,50^A0N,30,30^FD{item_name}^FS
^FO50,100^A0N,20,20^FDLOT: {lot_code}^FS
^FO50,130^A0N,20,20^FDQty: {quantity} {unit}^FS
^FO50,160^A0N,20,20^FDExp: {expiry_date}^FS
^FO50,200^BY3^BCN,50,Y,N,N^FD{lot_code}^FS
^XZ
"""
            
            return zpl.strip()
            
        except Exception as e:
            raise Exception(f"Failed to generate ZPL code: {str(e)}")
    
    @staticmethod
    def bulk_test_connections() -> Dict:
        """Test connections to all printers"""
        try:
            printers = Printer.query.all()
            results = []
            
            for printer in printers:
                result = PrinterService.test_printer_connection(printer.id)
                results.append(result)
            
            online_count = sum(1 for r in results if r['status'] == 'online')
            offline_count = len(results) - online_count
            
            return {
                'total_tested': len(results),
                'online_count': online_count,
                'offline_count': offline_count,
                'results': results,
                'message': f'Tested {len(results)} printers: {online_count} online, {offline_count} offline'
            }
            
        except Exception as e:
            raise Exception(f"Failed to bulk test printer connections: {str(e)}")
