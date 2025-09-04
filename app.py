from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
import os
import qrcode
import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
import uuid
import config
import socket
import time
import struct

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# Database Models
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    item_code = db.Column(db.String(20), unique=True, nullable=False)  # Numerical item code
    gtin = db.Column(db.String(14), unique=True, nullable=False)
    category = db.Column(db.String(50))  # New field for item categorization
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    lots = db.relationship('Lot', backref='item', lazy=True)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    lots = db.relationship('Lot', backref='vendor', lazy=True)

class Lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_code = db.Column(db.String(50), unique=True, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=True)  # New field for vendor tracking
    quantity = db.Column(db.Integer, default=0)
    expiry_date = db.Column(db.Date, default=lambda: (datetime.now(timezone.utc) + timedelta(days=10)).date())  # Auto 10 days
    receiving_date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())  # New field for receiving date
    notes = db.Column(db.Text)  # New field for LOT notes
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='active')  # active, expired, consumed

# Printer Configuration Model
class Printer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    port = db.Column(db.Integer, default=9100)
    printer_type = db.Column(db.String(50), default='zebra')
    label_width = db.Column(db.Float, default=4.0)
    label_height = db.Column(db.Float, default=2.0)
    dpi = db.Column(db.Integer, default=203)
    status = db.Column(db.String(20), default='offline')
    last_seen = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/label-designer')
def label_designer():
    return render_template('label_designer.html')

@app.route('/receiving')
def receiving():
    return render_template('receiving.html')

@app.route('/api/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'item_code': item.item_code,
        'gtin': item.gtin,
        'category': item.category,
        'created_at': item.created_at.isoformat(),
        'lot_count': len(item.lots)
    } for item in items])

@app.route('/api/items', methods=['POST'])
def create_item():
    data = request.json
    try:
        item = Item(
            name=data['name'],
            description=data.get('description', ''),
            item_code=data['item_code'],
            gtin=data['gtin'],
            category=data.get('category', '')
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({'success': True, 'id': item.id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/lots', methods=['GET'])
def get_lots():
    lots = Lot.query.all()
    return jsonify([{
        'id': lot.id,
        'lot_code': lot.lot_code,
        'item_name': lot.item.name,
        'item_code': lot.item.item_code,
        'item_gtin': lot.item.gtin,
        'quantity': lot.quantity,
        'expiry_date': lot.expiry_date.isoformat() if lot.expiry_date else None,
        'receiving_date': lot.receiving_date.isoformat() if lot.receiving_date else None,
        'vendor_name': lot.vendor.name if lot.vendor else None,
        'vendor_id': lot.vendor_id,
        'notes': lot.notes,
        'created_at': lot.created_at.isoformat(),
        'status': lot.status
    } for lot in lots])

@app.route('/api/lots', methods=['POST'])
def create_lot():
    data = request.json
    try:
        # Generate unique LOT code
        lot_code = generate_lot_code(data['item_id'])
        
        lot = Lot(
            lot_code=lot_code,
            item_id=data['item_id'],
            quantity=data.get('quantity', 0),
            expiry_date=datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data.get('expiry_date') else None,  # Auto-generated if not provided
            notes=data.get('notes', '')
        )
        db.session.add(lot)
        db.session.commit()
        return jsonify({'success': True, 'lot_code': lot_code}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/lots/<lot_code>/label')
def generate_label(lot_code):
    """Generate a Palumbo-style label with GS1-128 barcode"""
    return generate_palumbo_style_label(lot_code)

@app.route('/api/lots/<lot_code>/label/pti')
def generate_pti_label(lot_code):
    """Generate a PTI FSMA compliant label"""
    return generate_pti_fsma_label(lot_code)

# New ZPL endpoints
@app.route('/api/lots/<lot_code>/zpl')
def generate_zpl_label(lot_code):
    """Generate ZPL code for a LOT"""
    lot = Lot.query.filter_by(lot_code=lot_code).first()
    if not lot:
        return jsonify({'error': 'Lot not found'}), 404
    
    zpl_code = generate_palumbo_zpl(lot)
    return jsonify({
        'lot_code': lot_code,
        'zpl_code': zpl_code,
        'printer_ready': True
    })

@app.route('/api/lots/<lot_code>/zpl/pti')
def generate_pti_zpl_label(lot_code):
    """Generate PTI FSMA compliant ZPL code for a LOT"""
    lot = Lot.query.filter_by(lot_code=lot_code).first()
    if not lot:
        return jsonify({'error': 'Lot not found'}), 404
    
    zpl_code = generate_pti_zpl(lot)
    return jsonify({
        'lot_code': lot_code,
        'zpl_code': zpl_code,
        'printer_ready': True
    })

@app.route('/api/lots/<lot_code>/zpl/pti-voice-pick')
def generate_pti_voice_pick_zpl_label(lot_code):
    """Generate PTI FSMA compliant ZPL code with Voice Pick Code for a LOT"""
    lot = Lot.query.filter_by(lot_code=lot_code).first()
    if not lot:
        return jsonify({'error': 'Lot not found'}), 404
    
    zpl_code = generate_pti_voice_pick_zpl(lot)
    
    # Calculate Voice Pick Code for response
    voice_pick_code = calculate_voice_pick_code(
        lot.item.gtin, 
        lot.lot_code, 
        datetime.now(timezone.utc)
    )
    
    return jsonify({
        'lot_code': lot_code,
        'zpl_code': zpl_code,
        'voice_pick_code': voice_pick_code,
        'pti_compliant': True,
        'printer_ready': True
    })

@app.route('/api/lots/<lot_code>/print', methods=['POST'])
def print_label_direct(lot_code):
    """Print label directly to printer via IP"""
    data = request.json
    printer_id = data.get('printer_id')
    template = data.get('template', 'palumbo')
    
    if not printer_id:
        return jsonify({'error': 'Printer ID required'}), 400
    
    printer = db.session.get(Printer, printer_id)
    if not printer:
        return jsonify({'error': 'Printer not found'}), 404
    
    lot = Lot.query.filter_by(lot_code=lot_code).first()
    if not lot:
        return jsonify({'error': 'Lot not found'}), 404
    
    try:
        # Generate ZPL based on template
        if template == 'pti':
            zpl_code = generate_pti_zpl(lot)
        elif template == 'pti-voice-pick':
            zpl_code = generate_pti_voice_pick_zpl(lot)
        else:
            zpl_code = generate_palumbo_zpl(lot)
        
        # Send to printer
        success = send_zpl_to_printer(printer, zpl_code)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Label sent to {printer.name} ({printer.ip_address})',
                'printer': printer.name,
                'ip': printer.ip_address
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to send to printer {printer.name}'
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Enhanced batch printing endpoint
@app.route('/api/lots/batch/labels', methods=['POST'])
def generate_batch_labels():
    """Generate multiple labels for batch printing"""
    data = request.json
    lot_codes = data.get('lot_codes', [])
    template = data.get('template', 'palumbo')
    copies = data.get('copies', 1)
    
    if not lot_codes:
        return jsonify({'error': 'No LOT codes provided'}), 400
    
    # Create combined PDF with multiple labels
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Calculate layout for multiple labels per page
    labels_per_page = 4  # 2x2 grid
    page_width = 8.5 * inch
    page_height = 11 * inch
    label_width = 4.0 * inch
    label_height = 2.0 * inch
    margin = 0.25 * inch
    
    current_page = 0
    labels_on_current_page = 0
    
    for lot_code in lot_codes:
        lot = Lot.query.filter_by(lot_code=lot_code).first()
        if not lot:
            continue
            
        # Generate copies for this LOT
        for copy in range(copies):
            # Check if we need a new page
            if labels_on_current_page >= labels_per_page:
                p.showPage()
                current_page += 1
                labels_on_current_page = 0
            
            # Calculate position for this label
            row = labels_on_current_page // 2
            col = labels_on_current_page % 2
            x = margin + col * (label_width + margin)
            y = page_height - margin - (row + 1) * (label_height + margin)
            
            # Draw label border
            p.setStrokeColor(colors.black)
            p.setLineWidth(1)
            p.rect(x, y, label_width, label_height)
            
            # Add label content based on template
            if template == 'pti':
                draw_pti_label_content(p, lot, x, y, label_width, label_height)
            else:
                draw_palumbo_label_content(p, lot, x, y, label_width, label_height)
            
            labels_on_current_page += 1
    
    p.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"batch_labels_{template}_{len(lot_codes)}.pdf",
        mimetype='application/pdf'
    )

# New batch ZPL printing endpoint
@app.route('/api/lots/batch/print', methods=['POST'])
def print_batch_zpl():
    """Print multiple labels directly to printer via ZPL"""
    data = request.json
    lot_codes = data.get('lot_codes', [])
    printer_id = data.get('printer_id')
    template = data.get('template', 'palumbo')
    copies = data.get('copies', 1)
    
    if not lot_codes:
        return jsonify({'error': 'No LOT codes provided'}), 400
    
    if not printer_id:
        return jsonify({'error': 'Printer ID required'}), 400
    
    printer = db.session.get(Printer, printer_id)
    if not printer:
        return jsonify({'error': 'Printer not found'}), 404
    
    try:
        success_count = 0
        failed_lots = []
        
        for lot_code in lot_codes:
            lot = Lot.query.filter_by(lot_code=lot_code).first()
            if not lot:
                failed_lots.append(f"{lot_code}: Lot not found")
                continue
            
            # Generate ZPL based on template
            if template == 'pti':
                zpl_code = generate_pti_zpl(lot)
            else:
                zpl_code = generate_palumbo_zpl(lot)
            
            # Send to printer
            success = send_zpl_to_printer(printer, zpl_code)
            
            if success:
                success_count += 1
                # If multiple copies, send additional copies
                for _ in range(copies - 1):
                    send_zpl_to_printer(printer, zpl_code)
                    success_count += 1
            else:
                failed_lots.append(f"{lot_code}: Printer communication failed")
        
        return jsonify({
            'success': True,
            'message': f'Batch print completed: {success_count} labels sent to {printer.name}',
            'success_count': success_count,
            'failed_lots': failed_lots,
            'printer': printer.name,
            'ip': printer.ip_address
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Printer management endpoints
@app.route('/api/printers', methods=['GET'])
def get_printers():
    """Get all configured printers"""
    printers = Printer.query.all()
    return jsonify([{
        'id': printer.id,
        'name': printer.name,
        'ip_address': printer.ip_address,
        'port': printer.port,
        'printer_type': printer.printer_type,
        'label_width': printer.label_width,
        'label_height': printer.label_height,
        'dpi': printer.dpi,
        'status': printer.status,
        'last_seen': printer.last_seen.isoformat() if printer.last_seen else None
    } for printer in printers])

@app.route('/api/printers', methods=['POST'])
def create_printer():
    """Create a new printer configuration"""
    data = request.json
    try:
        printer = Printer(
            name=data['name'],
            ip_address=data['ip_address'],
            port=data.get('port', 9100),
            printer_type=data.get('printer_type', 'zebra'),
            label_width=data.get('label_width', 4.0),
            label_height=data.get('label_height', 2.0),
            dpi=data.get('dpi', 203)
        )
        db.session.add(printer)
        db.session.commit()
        return jsonify({'success': True, 'id': printer.id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/printers/<int:printer_id>/test', methods=['POST'])
def test_printer(printer_id):
    """Test printer connectivity and send test label"""
    printer = Printer.query.get_or_404(printer_id)
    
    try:
        # Generate test ZPL
        test_zpl = generate_test_zpl(printer)
        
        # Send to printer
        success = send_zpl_to_printer(printer, test_zpl)
        
        if success:
            # Update printer status
            printer.status = 'online'
            printer.last_seen = datetime.now(timezone.utc)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Test label sent successfully to {printer.name}',
                'printer_status': 'online'
            })
        else:
            printer.status = 'offline'
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': f'Failed to communicate with printer {printer.name}',
                'printer_status': 'offline'
            }), 500
            
    except Exception as e:
        printer.status = 'offline'
        db.session.commit()
        return jsonify({'success': False, 'error': str(e)}), 500

def draw_palumbo_label_content(p, lot, x, y, width, height):
    """Draw Palumbo-style label content at specific coordinates"""
    # Company header
    p.setFont("Helvetica-Bold", 10)
    p.drawString(x + 0.1*inch, y + height - 0.2*inch, config.COMPANY_NAME)
    p.setFont("Helvetica", 7)
    p.drawString(x + 0.1*inch, y + height - 0.35*inch, config.COMPANY_ADDRESS)
    
    # Product info
    p.setFont("Helvetica-Bold", 9)
    product_text = f"{lot.quantity} / {lot.item.name}"
    p.drawString(x + 0.1*inch, y + height - 0.55*inch, product_text)
    
    # GTIN and LOT
    p.setFont("Helvetica", 8)
    p.drawString(x + 0.1*inch, y + height - 0.75*inch, f"{lot.item.gtin[-6:]}")
    p.drawString(x + width - 1.2*inch, y + height - 0.75*inch, f"Lot#: {lot.lot_code[-6:]}")
    
    # Barcode area placeholder
    p.rect(x + 0.1*inch, y + 0.2*inch, width - 0.2*inch, 0.3*inch)
    p.setFont("Helvetica", 6)
    p.drawString(x + 0.1*inch, y + 0.15*inch, f"(01) {lot.item.gtin}")
    p.drawString(x + 0.1*inch, y + 0.05*inch, f"(15) {lot.created_at.strftime('%y%m%d')}")
    p.drawString(x + 0.1*inch, y - 0.05*inch, f"(10) {lot.lot_code}")
    
    # Quantity
    p.setFont("Helvetica-Bold", 8)
    p.drawString(x + 0.1*inch, y + 0.1*inch, f"{lot.quantity}")
    
    # QR code placeholder
    p.rect(x + width - 0.8*inch, y + 0.1*inch, 0.6*inch, 0.6*inch)
    p.setFont("Helvetica", 4)
    p.drawString(x + width - 0.75*inch, y + 0.4*inch, "QR")

def draw_pti_label_content(p, lot, x, y, width, height):
    """Draw PTI FSMA label content at specific coordinates"""
    # PTI Header
    p.setFont("Helvetica-Bold", 12)
    p.drawString(x + 0.1*inch, y + height - 0.2*inch, "PTI FSMA COMPLIANT")
    p.setFont("Helvetica-Bold", 9)
    p.drawString(x + 0.1*inch, y + height - 0.4*inch, config.COMPANY_NAME)
    
    # Product info
    p.setFont("Helvetica-Bold", 10)
    p.drawString(x + 0.1*inch, y + height - 0.6*inch, f"Product: {lot.item.name}")
    p.setFont("Helvetica", 8)
    p.drawString(x + 0.1*inch, y + height - 0.8*inch, f"GTIN: {lot.item.gtin}")
    
    # LOT and date
    p.drawString(x + 0.1*inch, y + height - 1.0*inch, f"LOT: {lot.lot_code}")
    p.drawString(x + 0.1*inch, y + height - 1.2*inch, f"Pack Date: {lot.created_at.strftime('%m/%d/%y')}")
    
    # Quantity
    p.drawString(x + 0.1*inch, y + height - 1.4*inch, f"Quantity: {lot.quantity}")
    
    # Barcode area
    p.rect(x + 0.1*inch, y + 0.1*inch, width - 0.2*inch, 0.25*inch)
    p.setFont("Helvetica", 6)
    p.drawString(x + 0.1*inch, y + 0.05*inch, f"(01) {lot.item.gtin}")
    p.drawString(x + 0.1*inch, y - 0.05*inch, f"(15) {lot.created_at.strftime('%y%m%d')}")
    p.drawString(x + 0.1*inch, y - 0.15*inch, f"(10) {lot.lot_code}")

# ZPL Generation Functions
def generate_palumbo_zpl(lot):
    """Generate Palumbo-style ZPL code matching the working format"""
    # Get current date in YYMMDD format
    current_date = datetime.now(timezone.utc).strftime('%y%m%d')
    
    # Create GS1-128 barcode data with proper format
    # Format: (01)GTIN(15)Date(10)LOT
    gtin = lot.item.gtin
    lot_short = lot.lot_code[-6:] if len(lot.lot_code) > 6 else lot.lot_code
    
    # Create the barcode data string
    barcode_data = f">;01{gtin}15{current_date}10{lot_short}0000"
    
    # Generate ZPL matching the working format
    zpl = f"""^XA^MMT^MNY^PW812^LL710^FWN^^FT30,40^FB750,1,,C^A0,30^FD{config.COMPANY_NAME}^FS
^FT30,80^FB750,1,,C^A0,30^FD{config.COMPANY_ADDRESS}^FS
^FT30,180^FB750,2,2,L^A0,45^FD{lot.item.name}^FS
^FT50,240^A0,45^FD{current_date}^FS
^FT500,240^A0,45^FDLot#: {lot_short}^FS
^BY2,2^FO135,255^BCN,55,N,N,N,N^FD{barcode_data}^FS
^FO10,320,2^FB750,1,,C^A0,23^FD(01) {gtin} (15) {current_date} (10) {lot_short} 0000^FS
^FT30,390^A0,50^FD{lot.quantity}^FS
^XZ"""
    
    return zpl

def generate_pti_zpl(lot):
    """Generate PTI FSMA compliant ZPL code matching the working format"""
    # Get current date in YYMMDD format
    current_date = datetime.now(timezone.utc).strftime('%y%m%d')
    
    # Create GS1-128 barcode data with proper format
    # Format: (01)GTIN(15)Date(10)LOT
    gtin = lot.item.gtin
    lot_short = lot.lot_code[-6:] if len(lot.lot_code) > 6 else lot.lot_code
    
    # Create the barcode data string
    barcode_data = f">;01{gtin}15{current_date}10{lot_short}0000"
    
    # Generate ZPL matching the working format but with PTI FSMA header
    zpl = f"""^XA^MMT^MNY^PW812^LL710^FWN^^FT30,40^FB750,1,,C^A0,30^FDPTI FSMA COMPLIANT^FS
^FT30,80^FB750,1,,C^A0,30^FD{config.COMPANY_NAME}^FS
^FT30,120^FB750,1,,C^A0,30^FD{config.COMPANY_ADDRESS}^FS
^FT30,180^FB750,2,2,L^A0,45^FD{lot.item.name}^FS
^FT50,240^A0,45^FD{current_date}^FS
^FT500,240^A0,45^FDLot#: {lot_short}^FS
^BY2,2^FO135,255^BCN,55,N,N,N,N^FD{barcode_data}^FS
^FO10,320,2^FB750,1,,C^A0,23^FD(01) {gtin} (15) {current_date} (10) {lot_short} 0000^FS
^FT30,390^A0,50^FD{lot.quantity}^FS
^XZ"""
    
    return zpl

def calculate_voice_pick_code(gtin, lot_code, pack_date=None):
    """
    Calculate PTI Voice Pick Code using ANSI CRC-16 algorithm
    
    According to PTI specification:
    1. PlainText = GTIN + Lot + Date (YYMMDD format)
    2. Compute ANSI CRC-16 hash with polynomial X^16 + X^15 + X^2 + 1
    3. Take 4 least significant digits (Hash mod 10000)
    
    Args:
        gtin (str): 14-digit GTIN
        lot_code (str): Lot code (1-20 alphanumeric characters)
        pack_date (datetime, optional): Pack date for date-specific codes
    
    Returns:
        str: 4-digit Voice Pick Code
    """
    # Step 1: Create PlainText (GTIN + Lot + Date)
    plain_text = gtin + lot_code
    
    if pack_date:
        # Format date as YYMMDD with zero padding
        date_str = pack_date.strftime('%y%m%d')
        plain_text += date_str
    
    # Step 2: Compute ANSI CRC-16 hash
    # Using the exact algorithm from PTI specification
    # Polynomial: X^16 + X^15 + X^2 + 1 = 0x8005 (reversed to 0xA001)
    polynomial = 0xA001
    crc = 0x0000
    
    for byte in plain_text.encode('ascii'):
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ polynomial
            else:
                crc >>= 1
    
    # Step 3: Take 4 least significant digits
    voice_pick_code = f"{crc % 10000:04d}"
    
    return voice_pick_code

def generate_pti_voice_pick_zpl(lot):
    """
    Generate PTI FSMA compliant ZPL code with Voice Pick Code
    
    This follows the PTI specification for enhanced traceability labels
    including the Voice Pick Code for warehouse operations.
    """
    # Get current date in YYMMDD format
    current_date = datetime.now(timezone.utc)
    date_str = current_date.strftime('%y%m%d')
    
    # Calculate Voice Pick Code
    voice_pick_code = calculate_voice_pick_code(
        lot.item.gtin, 
        lot.lot_code, 
        current_date
    )
    
    # Create GS1-128 barcode data with proper format
    # Format: (01)GTIN(15)Date(10)LOT
    gtin = lot.item.gtin
    lot_short = lot.lot_code[-6:] if len(lot.lot_code) > 6 else lot.lot_code
    
    # Create the barcode data string
    barcode_data = f">;01{gtin}15{date_str}10{lot_short}0000"
    
    # Generate ZPL with Voice Pick Code prominently displayed
    # Voice Pick Code is displayed with 2 large digits (least significant) 
    # and 2 small digits (most significant) as per PTI spec
    zpl = f"""^XA^MMT^MNY^PW812^LL710^FWN^^FT30,40^FB750,1,,C^A0,30^FD{config.COMPANY_NAME}^FS
^FT30,80^FB750,1,,C^A0,30^FD{config.COMPANY_ADDRESS}^FS
^FT30,180^FB750,2,2,L^A0,45^FD{lot.item.description or lot.item.name}^FS
^FT50,240^A0,45^FD{date_str}^FS
^FT500,240^A0,45^FDLot#: {lot_short}^FS

^BY2,2^FO135,255^BCN,55,N,N,N,N^FD{barcode_data}^FS
^FO10,320,2^FB750,1,,C^A0,23^FD(01) {gtin} (15) {date_str} (10) {lot_short} 0000^FS

^FT30,390^A0,50^FD{lot.item.item_code}^FS

^FT650,350^A0,25^FDVoice Pick Code:^FS
^FT700,380^A0,35^FD{voice_pick_code[:2]}^FS
^FT750,380^A0,25^FD{voice_pick_code[2:]}^FS
^XZ"""
    
    return zpl

def generate_test_zpl(printer):
    """Generate test ZPL label for printer testing"""
    dpi = printer.dpi
    label_width = int(printer.label_width * dpi)
    label_height = int(printer.label_height * dpi)
    
    zpl = f"""^XA
^FO50,50^A0N,50,50^FDTest Label^FS
^FO50,120^A0N,30,30^FDPrinter: {printer.name}^FS
^FO50,160^A0N,30,30^FDIP: {printer.ip_address}^FS
^FO50,200^A0N,30,30^FDTime: {datetime.now().strftime('%H:%M:%S')}^FS
^FO50,240^A0N,30,30^FDDate: {datetime.now().strftime('%m/%d/%Y')}^FS
^FO50,280^BY3^BCN,100,Y,N,N^FD123456789012345^FS
^XZ"""
    
    return zpl

def send_zpl_to_printer(printer, zpl_code):
    """Send ZPL code directly to printer via IP"""
    try:
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # 10 second timeout
        
        # Connect to printer
        sock.connect((printer.ip_address, printer.port))
        
        # Send ZPL code
        sock.send(zpl_code.encode('utf-8'))
        
        # Wait a moment for processing
        time.sleep(0.5)
        
        # Close connection
        sock.close()
        
        return True
        
    except Exception as e:
        print(f"Error sending to printer {printer.name}: {str(e)}")
        return False

@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify({
        'id': item.id,
        'name': item.name,
        'item_code': item.item_code,
        'gtin': item.gtin,
        'description': item.description,
        'category': getattr(item, 'category', None),
        'created_at': item.created_at.isoformat()
    })

@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json()
    
    if 'name' in data:
        item.name = data['name']
    if 'item_code' in data:
        item.item_code = data['item_code']
    if 'gtin' in data:
        item.gtin = data['gtin']
    if 'description' in data:
        item.description = data['description']
    if 'category' in data:
        item.category = data['category']
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    # Check if item has associated lots
    lots = Lot.query.filter_by(item_id=item_id).all()
    if lots:
        return jsonify({'success': False, 'error': 'Cannot delete item with associated LOT codes'}), 400
    
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/lots/<lot_code>', methods=['GET'])
def get_lot(lot_code):
    lot = Lot.query.filter_by(lot_code=lot_code).first_or_404()
    return jsonify({
        'lot_code': lot.lot_code,
        'item_id': lot.item_id,
        'quantity': lot.quantity,
        'expiry_date': lot.expiry_date.isoformat() if lot.expiry_date else None,
        'notes': getattr(lot, 'notes', None),
        'created_at': lot.created_at.isoformat()
    })

@app.route('/api/lots/<lot_code>', methods=['PUT'])
def update_lot(lot_code):
    lot = Lot.query.filter_by(lot_code=lot_code).first_or_404()
    data = request.get_json()
    
    if 'item_id' in data:
        lot.item_id = data['item_id']
    if 'quantity' in data:
        lot.quantity = data['quantity']
    if 'expiry_date' in data:
        lot.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data['expiry_date'] else None
    if 'notes' in data:
        lot.notes = data['notes']
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'LOT code updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/lots/<lot_code>', methods=['DELETE'])
def delete_lot(lot_code):
    lot = Lot.query.filter_by(lot_code=lot_code).first_or_404()
    
    try:
        db.session.delete(lot)
        db.session.commit()
        return jsonify({'success': True, 'message': 'LOT code deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

def generate_palumbo_style_label(lot_code):
    lot = Lot.query.filter_by(lot_code=lot_code).first()
    if not lot:
        return jsonify({'error': 'Lot not found'}), 404
    
    # Create PDF label
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Label dimensions (Zebra label format)
    label_width = config.LABEL_WIDTH * inch
    label_height = config.LABEL_HEIGHT * inch
    
    # Draw border with rounded corners effect
    p.setStrokeColor(colors.black)
    p.setLineWidth(1)
    p.rect(config.LABEL_MARGIN*inch, config.LABEL_MARGIN*inch, label_width, label_height)
    
    # Company header section (like Palumbo Foods)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(0.2*inch, 1.8*inch, config.COMPANY_NAME)
    p.setFont("Helvetica", 8)
    p.drawString(0.2*inch, 1.65*inch, config.COMPANY_ADDRESS)
    
    # Product description section (like "12 / 8 oz Whole White")
    p.setFont("Helvetica-Bold", 11)
    product_text = f"{lot.quantity} / {lot.item.name}"
    p.drawString(0.2*inch, 1.45*inch, product_text)
    
    # Item code and LOT number section (like "250903" and "Lot#: 107733")
    p.setFont("Helvetica", 10)
    p.drawString(0.2*inch, 1.25*inch, f"{lot.item.gtin[-6:]}")  # Last 6 digits of GTIN
    p.drawString(2.2*inch, 1.25*inch, f"Lot#: {lot.lot_code[-6:]}")  # Last 6 digits of LOT
    
    # Generate GS1-128 barcode data (PTI FSMA compliant)
    barcode_data = f"(01){lot.item.gtin}(15){lot.created_at.strftime('%y%m%d')}(10){lot.lot_code}"
    
    # Create GS1-128 barcode
    try:
        # Generate barcode image
        barcode_class = barcode.get_barcode_class('code128')
        barcode_img = barcode_class(barcode_data, writer=ImageWriter())
        barcode_buffer = BytesIO()
        barcode_img.save(barcode_buffer, format='PNG')
        barcode_buffer.seek(0)
        
        # Add barcode to PDF
        # Convert BytesIO to a temporary file path for reportlab
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(barcode_buffer.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            p.drawImage(tmp_file_path, 0.2*inch, 0.8*inch, width=3.5*inch, height=0.3*inch)
        finally:
            # Clean up temporary file
            import os
            os.unlink(tmp_file_path)
        
        # Barcode data labels below the barcode (like in your photo)
        p.setFont("Helvetica", 7)
        p.drawString(0.2*inch, 0.6*inch, f"(01) {lot.item.gtin}")
        p.drawString(0.2*inch, 0.5*inch, f"(15) {lot.created_at.strftime('%y%m%d')}")
        p.drawString(0.2*inch, 0.4*inch, f"(10) {lot.lot_code}")
        
    except Exception as e:
        # Fallback to text representation if barcode generation fails
        p.setFont("Helvetica", 7)
        p.drawString(0.2*inch, 0.8*inch, "Barcode:")
        p.drawString(0.2*inch, 0.7*inch, barcode_data)
        p.drawString(0.2*inch, 0.6*inch, f"(01) {lot.item.gtin}")
        p.drawString(0.2*inch, 0.5*inch, f"(15) {lot.created_at.strftime('%y%m%d')}")
        p.drawString(0.2*inch, 0.4*inch, f"(10) {lot.lot_code}")
    
    # Quantity in bottom left (like "1500" in your photo)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(0.2*inch, 0.2*inch, f"{lot.quantity}")
    
    # Generate QR code with GS1 data
    qr_data = f"GTIN:{lot.item.gtin}\nLOT:{lot.lot_code}\nQTY:{lot.quantity}\nDATE:{lot.created_at.strftime('%Y%m%d')}"
    qr = qrcode.QRCode(version=config.QR_VERSION, box_size=config.QR_BOX_SIZE, border=config.QR_BORDER)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Save QR code temporarily and add to PDF
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    # Add QR code to PDF (positioned on the right side)
    # Convert BytesIO to a temporary file path for reportlab
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        tmp_file.write(qr_buffer.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        p.drawImage(tmp_file_path, 3.2*inch, 0.2*inch, width=0.7*inch, height=0.7*inch)
    finally:
        # Clean up temporary file
        import os
        os.unlink(tmp_file_path)
    
    p.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"label_{lot_code}.pdf",
        mimetype='application/pdf'
    )

def generate_pti_fsma_label(lot_code):
    """Generate a PTI FSMA compliant label"""
    lot = Lot.query.filter_by(lot_code=lot_code).first()
    if not lot:
        return jsonify({'error': 'Lot not found'}), 404
    
    # Create PDF label
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Label dimensions (PTI standard)
    label_width = 4.0 * inch
    label_height = 2.5 * inch
    
    # Draw border
    p.setStrokeColor(colors.black)
    p.setLineWidth(1)
    p.rect(0.5*inch, 0.5*inch, label_width, label_height)
    
    # PTI FSMA Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(0.7*inch, 2.2*inch, "PTI FSMA COMPLIANT")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(0.7*inch, 2.0*inch, config.COMPANY_NAME)
    
    # Product Information
    p.setFont("Helvetica-Bold", 14)
    p.drawString(0.7*inch, 1.8*inch, f"Product: {lot.item.name}")
    p.setFont("Helvetica", 12)
    p.drawString(0.7*inch, 1.6*inch, f"GTIN: {lot.item.gtin}")
    
    # LOT and Date Information
    p.drawString(0.7*inch, 1.4*inch, f"LOT: {lot.lot_code}")
    p.drawString(0.7*inch, 1.2*inch, f"Pack Date: {lot.created_at.strftime('%m/%d/%y')}")
    
    # Quantity and Expiry
    p.drawString(0.7*inch, 1.0*inch, f"Quantity: {lot.quantity}")
    if lot.expiry_date:
        p.drawString(0.7*inch, 0.8*inch, f"Expiry: {lot.expiry_date.strftime('%m/%d/%y')}")
    
    # GS1-128 Barcode (PTI requirement)
    barcode_data = f"(01){lot.item.gtin}(15){lot.created_at.strftime('%y%m%d')}(10){lot.lot_code}"
    
    try:
        # Generate barcode image
        barcode_class = barcode.get_barcode_class('code128')
        barcode_img = barcode_class(barcode_data, writer=ImageWriter())
        barcode_buffer = BytesIO()
        barcode_img.save(barcode_buffer, format='PNG')
        barcode_buffer.seek(0)
        
        # Add barcode to PDF
        # Convert BytesIO to a temporary file path for reportlab
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(barcode_buffer.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            p.drawImage(tmp_file_path, 0.7*inch, 0.4*inch, width=3.0*inch, height=0.3*inch)
        finally:
            # Clean up temporary file
            import os
            os.unlink(tmp_file_path)
        
        # Barcode data labels
        p.setFont("Helvetica", 8)
        p.drawString(0.7*inch, 0.3*inch, f"(01) {lot.item.gtin}")
        p.drawString(0.7*inch, 0.2*inch, f"(15) {lot.created_at.strftime('%y%m%d')}")
        p.drawString(0.7*inch, 0.1*inch, f"(10) {lot.lot_code}")
        
    except Exception as e:
        # Fallback to text representation
        p.setFont("Helvetica", 8)
        p.drawString(0.7*inch, 0.4*inch, "Barcode: " + barcode_data)
    
    p.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"pti_label_{lot_code}.pdf",
        mimetype='application/pdf'
    )

def generate_lot_code(item_id):
    """Generate a unique LOT code based on item ID and timestamp"""
    timestamp = datetime.now(timezone.utc).strftime(config.LOT_TIMESTAMP_FORMAT)
    random_suffix = str(uuid.uuid4())[:config.LOT_RANDOM_SUFFIX_LENGTH].upper()
    return f"{config.LOT_PREFIX}{item_id:04d}{timestamp}{random_suffix}"

# Vendor Management API Endpoints
@app.route('/api/vendors', methods=['GET'])
def get_vendors():
    vendors = Vendor.query.all()
    return jsonify([{
        'id': vendor.id,
        'name': vendor.name,
        'contact_person': vendor.contact_person,
        'email': vendor.email,
        'phone': vendor.phone,
        'address': vendor.address,
        'created_at': vendor.created_at.isoformat() if vendor.created_at else None
    } for vendor in vendors])

@app.route('/api/vendors', methods=['POST'])
def create_vendor():
    data = request.get_json()
    vendor = Vendor(
        name=data['name'],
        contact_person=data.get('contact_person'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address')
    )
    db.session.add(vendor)
    db.session.commit()
    return jsonify({'id': vendor.id, 'message': 'Vendor created successfully'}), 201

@app.route('/api/vendors/<int:vendor_id>', methods=['PUT'])
def update_vendor(vendor_id):
    vendor = db.session.get(Vendor, vendor_id)
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404
    
    data = request.get_json()
    vendor.name = data.get('name', vendor.name)
    vendor.contact_person = data.get('contact_person', vendor.contact_person)
    vendor.email = data.get('email', vendor.email)
    vendor.phone = data.get('phone', vendor.phone)
    vendor.address = data.get('address', vendor.address)
    
    db.session.commit()
    return jsonify({'message': 'Vendor updated successfully'})

@app.route('/api/vendors/<int:vendor_id>', methods=['DELETE'])
def delete_vendor(vendor_id):
    vendor = db.session.get(Vendor, vendor_id)
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404
    
    db.session.delete(vendor)
    db.session.commit()
    return jsonify({'message': 'Vendor deleted successfully'})

# Receiving Workflow API Endpoints
@app.route('/api/receive', methods=['POST'])
def receive_product():
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['item_code', 'quantity', 'vendor_id']):
        return jsonify({'error': 'Missing required fields: item_code, quantity, vendor_id'}), 400
    
    # Find the item by item_code
    item = Item.query.filter_by(item_code=data['item_code']).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    # Find the vendor
    vendor = db.session.get(Vendor, data['vendor_id'])
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404
    
    # Generate lot code
    lot_code = generate_lot_code(item.id)
    
    # Create the lot
    lot = Lot(
        lot_code=lot_code,
        item_id=item.id,
        vendor_id=vendor.id,
        quantity=data['quantity'],
        receiving_date=datetime.now(timezone.utc).date(),
        notes=data.get('notes', '')
    )
    
    db.session.add(lot)
    db.session.commit()
    
    return jsonify({
        'lot_id': lot.id,
        'lot_code': lot.lot_code,
        'item_name': item.name,
        'vendor_name': vendor.name,
        'quantity': lot.quantity,
        'receiving_date': lot.receiving_date.isoformat(),
        'expiry_date': lot.expiry_date.isoformat(),
        'message': 'Product received successfully'
    }), 201

@app.route('/api/receive/batch', methods=['POST'])
def receive_products_batch():
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['items', 'vendor_id']):
        return jsonify({'error': 'Missing required fields: items, vendor_id'}), 400
    
    if not isinstance(data['items'], list) or len(data['items']) == 0:
        return jsonify({'error': 'Items must be a non-empty list'}), 400
    
    # Find the vendor
    vendor = db.session.get(Vendor, data['vendor_id'])
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404
    
    receiving_date = datetime.now(timezone.utc).date()
    received_lots = []
    errors = []
    
    try:
        for item_data in data['items']:
            # Validate item data
            if not all(k in item_data for k in ['item_code', 'quantity']):
                errors.append(f"Missing required fields for item: {item_data.get('item_code', 'unknown')}")
                continue
            
            # Find the item by item_code
            item = Item.query.filter_by(item_code=item_data['item_code']).first()
            if not item:
                errors.append(f"Item not found: {item_data['item_code']}")
                continue
            
            # Generate lot code
            lot_code = generate_lot_code(item.id)
            
            # Create the lot
            lot = Lot(
                lot_code=lot_code,
                item_id=item.id,
                vendor_id=vendor.id,
                quantity=item_data['quantity'],
                receiving_date=receiving_date,
                notes=item_data.get('notes', '')
            )
            
            db.session.add(lot)
            received_lots.append({
                'lot_id': lot.id,
                'lot_code': lot.lot_code,
                'item_name': item.name,
                'item_code': item.item_code,
                'quantity': lot.quantity,
                'expiry_date': lot.expiry_date.isoformat() if lot.expiry_date else None,
                'notes': lot.notes
            })
        
        if errors:
            return jsonify({'error': 'Some items failed to process', 'details': errors}), 400
        
        db.session.commit()
        
        return jsonify({
            'vendor_name': vendor.name,
            'vendor_id': vendor.id,
            'receiving_date': receiving_date.isoformat(),
            'total_items': len(received_lots),
            'lots': received_lots,
            'message': f'Successfully received {len(received_lots)} items from {vendor.name}'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to process receiving: {str(e)}'}), 500

@app.route('/api/receipt/<lot_code>', methods=['GET'])
def generate_receipt(lot_code):
    lot = Lot.query.filter_by(lot_code=lot_code).first()
    if not lot:
        return jsonify({'error': 'Lot not found'}), 404
    
    return jsonify({
        'lot_code': lot.lot_code,
        'item_name': lot.item.name,
        'item_code': lot.item.item_code,
        'vendor_name': lot.vendor.name if lot.vendor else 'Unknown',
        'quantity': lot.quantity,
        'receiving_date': lot.receiving_date.isoformat(),
        'expiry_date': lot.expiry_date.isoformat(),
        'notes': lot.notes
    })

@app.route('/api/receipt/vendor/<int:vendor_id>/<receiving_date>', methods=['GET'])
def generate_vendor_receipt(vendor_id, receiving_date):
    """Generate a vendor receipt for all items received on a specific date"""
    vendor = db.session.get(Vendor, vendor_id)
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404
    
    # Parse the receiving date
    try:
        date_obj = datetime.strptime(receiving_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Get all lots received from this vendor on this date
    lots = Lot.query.filter_by(
        vendor_id=vendor_id,
        receiving_date=date_obj
    ).all()
    
    if not lots:
        return jsonify({'error': 'No items found for this vendor on this date'}), 404
    
    # Calculate totals
    total_items = len(lots)
    total_quantity = sum(lot.quantity for lot in lots)
    
    return jsonify({
        'vendor': {
            'id': vendor.id,
            'name': vendor.name,
            'contact_person': vendor.contact_person,
            'email': vendor.email,
            'phone': vendor.phone,
            'address': vendor.address
        },
        'receiving_date': receiving_date,
        'total_items': total_items,
        'total_quantity': total_quantity,
        'items': [{
            'lot_code': lot.lot_code,
            'item_name': lot.item.name,
            'item_code': lot.item.item_code,
            'quantity': lot.quantity,
            'expiry_date': lot.expiry_date.isoformat(),
            'notes': lot.notes
        } for lot in lots]
    })

@app.route('/api/receipt/vendor/<int:vendor_id>/<receiving_date>/pdf', methods=['GET'])
def generate_vendor_receipt_pdf(vendor_id, receiving_date):
    """Generate a PDF vendor receipt"""
    vendor = db.session.get(Vendor, vendor_id)
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404
    
    # Parse the receiving date
    try:
        date_obj = datetime.strptime(receiving_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Get all lots received from this vendor on this date
    lots = Lot.query.filter_by(
        vendor_id=vendor_id,
        receiving_date=date_obj
    ).all()
    
    if not lots:
        return jsonify({'error': 'No items found for this vendor on this date'}), 404
    
    # Create PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Company Header
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, height - 40, config.COMPANY_NAME)
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 60, config.COMPANY_ADDRESS)
    
    # Receipt Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 90, "RECEIVING RECEIPT")
    
    # Receiving Information (moved to top right)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(400, height - 90, "Receiving Details:")
    p.setFont("Helvetica", 10)
    p.drawString(400, height - 110, f"Date: {receiving_date}")
    p.drawString(400, height - 125, f"Total Items: {len(lots)}")
    p.drawString(400, height - 140, f"Total Quantity: {sum(lot.quantity for lot in lots)}")
    
    # Vendor Information
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 130, "Vendor Information:")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 150, f"Name: {vendor.name}")
    if vendor.contact_person:
        p.drawString(50, height - 165, f"Contact: {vendor.contact_person}")
    if vendor.phone:
        p.drawString(50, height - 180, f"Phone: {vendor.phone}")
    if vendor.email:
        p.drawString(50, height - 195, f"Email: {vendor.email}")
    if vendor.address:
        p.drawString(50, height - 210, f"Address: {vendor.address}")
    
    # Items Table Header
    y_position = height - 250
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y_position, "Item Code")
    p.drawString(120, y_position, "Item Name")
    p.drawString(280, y_position, "Lot Code")
    p.drawString(420, y_position, "Quantity")
    p.drawString(480, y_position, "Expiry Date")
    
    # Draw line under header
    p.line(50, y_position - 5, 550, y_position - 5)
    
    # Items
    p.setFont("Helvetica", 9)
    y_position -= 20
    
    for lot in lots:
        if y_position < 200:  # Start new page if needed
            p.showPage()
            y_position = height - 50
        
        p.drawString(50, y_position, lot.item.item_code)
        p.drawString(120, y_position, lot.item.name[:25])  # Truncate long names
        p.drawString(280, y_position, lot.lot_code)
        p.drawString(420, y_position, str(lot.quantity))
        p.drawString(480, y_position, lot.expiry_date.strftime('%Y-%m-%d'))
        
        y_position -= 15
    
    # Signature Section
    signature_y = max(y_position - 50, 150)  # Ensure enough space for signature
    
    # Draw signature line
    p.setFont("Helvetica", 10)
    p.drawString(50, signature_y, "Received by:")
    p.line(50, signature_y - 5, 250, signature_y - 5)
    
    p.drawString(300, signature_y, "Date:")
    p.line(300, signature_y - 5, 450, signature_y - 5)
    
    # Company signature line
    p.drawString(50, signature_y - 30, "Authorized by:")
    p.line(50, signature_y - 35, 250, signature_y - 35)
    
    p.drawString(300, signature_y - 30, "Date:")
    p.line(300, signature_y - 35, 450, signature_y - 35)
    
    # Footer
    p.setFont("Helvetica", 8)
    p.drawString(50, 50, f"Generated on: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    p.drawString(50, 35, f"Receipt ID: {vendor.id}-{receiving_date.replace('-', '')}-{len(lots)}")
    
    p.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"receipt_{vendor.name.replace(' ', '_')}_{receiving_date}.pdf",
        mimetype='application/pdf'
    )

@app.route('/api/search')
def search():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
    # Search in items
    items = Item.query.filter(
        db.or_(
            Item.name.ilike(f'%{query}%'),
            Item.item_code.ilike(f'%{query}%'),
            Item.gtin.ilike(f'%{query}%'),
            Item.description.ilike(f'%{query}%')
        )
    ).all()
    
    # Search in lots
    lots = Lot.query.filter(
        db.or_(
            Lot.lot_code.ilike(f'%{query}%')
        )
    ).all()
    
    results = []
    
    for item in items:
        results.append({
            'type': 'item',
            'id': item.id,
            'name': item.name,
            'item_code': item.item_code,
            'gtin': item.gtin,
            'description': item.description
        })
    
    for lot in lots:
        results.append({
            'type': 'lot',
            'id': lot.id,
            'lot_code': lot.lot_code,
            'item_name': lot.item.name,
            'gtin': lot.item.gtin
        })
    
    return jsonify(results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
