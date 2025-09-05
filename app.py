from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
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
from PIL import Image
import json
import threading
import secrets
from decimal import Decimal
import requests
from version import VERSION_INFO, VERSION, COMMIT_HASH, BRANCH, BUILD_DATE
from changelog import (
    load_changelog, get_version_changelog, get_latest_changelog, 
    get_all_versions, get_changelog_summary, CHANGELOG_DATA
)

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Optimize for concurrent users
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 20,
    'max_overflow': 0
}

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)
CORS(app)

# Context processor to make version info available to all templates
@app.context_processor
def inject_version_info():
    return {
        'version_info': VERSION_INFO,
        'app_version': VERSION,
        'commit_hash': COMMIT_HASH,
        'branch': BRANCH,
        'build_date': BUILD_DATE
    }

# Import threading for concurrent operations
import threading
from functools import wraps

# Global locks for concurrent operations
print_queue_lock = threading.Lock()
database_lock = threading.Lock()

# Active user sessions tracking
active_sessions = {}
session_lock = threading.Lock()

# Rate limiting
from collections import defaultdict, deque
import time

# Rate limiting storage
rate_limits = defaultdict(lambda: deque())
rate_limit_lock = threading.Lock()

# Simple in-memory cache
cache = {}
cache_lock = threading.Lock()
CACHE_TTL = 300  # 5 minutes

def rate_limit(max_requests=60, window=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            client_ip = request.remote_addr
            current_time = time.time()
            
            with rate_limit_lock:
                # Clean old requests
                while rate_limits[client_ip] and rate_limits[client_ip][0] < current_time - window:
                    rate_limits[client_ip].popleft()
                
                # Check if limit exceeded
                if len(rate_limits[client_ip]) >= max_requests:
                    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
                
                # Add current request
                rate_limits[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_from_cache(key):
    """Get value from cache if not expired"""
    with cache_lock:
        if key in cache:
            value, timestamp = cache[key]
            if time.time() - timestamp < CACHE_TTL:
                return value
            else:
                del cache[key]
    return None

def set_cache(key, value):
    """Set value in cache with timestamp"""
    with cache_lock:
        cache[key] = (value, time.time())

def clear_cache():
    """Clear all cache entries"""
    with cache_lock:
        cache.clear()

# QuickBooks Online Configuration
QB_CLIENT_ID = os.getenv('QB_CLIENT_ID', 'ABUW0U3AsMTGyq7bb1ujpj17IodZlrGkMYtjaWGfke6gcztmtY')
QB_CLIENT_SECRET = os.getenv('QB_CLIENT_SECRET', 'H75cxmzTruVA2LpU27IyAUzJKJlsNgWHMrJaz3MN')
QB_REDIRECT_URI = os.getenv('QB_REDIRECT_URI', 'http://localhost:5001/qb/callback')
QB_SCOPE = 'com.intuit.quickbooks.accounting'
QB_DISCOVERY_DOCUMENT = 'https://appcenter.intuit.com/api/v1/OpenID/QBOpenID'
QB_BASE_URL = 'https://sandbox-quickbooks.api.intuit.com'  # Use sandbox for testing
QB_COMPANY_ID = os.getenv('QB_COMPANY_ID', '9341455300640805')  # Sandbox Company ID for testing

# QuickBooks helper functions
def generate_order_number():
    """Generate a unique order number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = secrets.token_hex(2).upper()
    return f"ORD-{timestamp}-{random_suffix}"

def calculate_order_totals(order_items):
    """Calculate order totals from order items"""
    subtotal = sum(float(item['total_price']) for item in order_items)
    tax_rate = 0.0875  # 8.75% tax rate - should be configurable
    tax_amount = subtotal * tax_rate
    total_amount = subtotal + tax_amount
    return {
        'subtotal': round(subtotal, 2),
        'tax_amount': round(tax_amount, 2),
        'total_amount': round(total_amount, 2)
    }

# QuickBooks API helper functions
def get_qb_access_token():
    """Get QuickBooks access token from session or storage"""
    # In a real implementation, you'd store this securely
    # For now, we'll use a placeholder
    return session.get('qb_access_token')

def make_qb_api_request(endpoint, method='GET', data=None):
    """Make authenticated request to QuickBooks API"""
    access_token = get_qb_access_token()
    if not access_token:
        return {'error': 'No QuickBooks access token found'}
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # QuickBooks API URL structure
    # For company info: /v3/company/{companyId}/companyinfo/{companyId}
    # For queries: /v3/company/{companyId}/query?query=<selectStatement>&minorversion=75
    
    if endpoint == 'companyinfo/1':
        # Special case for company info
        url = f"{QB_BASE_URL}/v3/company/{QB_COMPANY_ID}/companyinfo/{QB_COMPANY_ID}"
    else:
        # Standard endpoint structure - endpoint may include query parameters
        url = f"{QB_BASE_URL}/v3/company/{QB_COMPANY_ID}/{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        else:
            return {'error': f'Unsupported method: {method}'}
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'error': f'QuickBooks API error: {str(e)}'}

def import_qb_customers():
    """Import customers from QuickBooks"""
    try:
        # Get customers from QuickBooks using query endpoint
        query = "SELECT * FROM Customer"
        result = make_qb_api_request(f'query?query={query}&minorversion=75')
        if 'error' in result:
            return result
        
        customers_imported = 0
        customers_updated = 0
        errors = []
        
        for qb_customer in result.get('QueryResponse', {}).get('Customer', []):
            try:
                # Extract customer data from QB response with fallbacks
                customer_data = {
                    'name': qb_customer.get('Name') or qb_customer.get('DisplayName') or qb_customer.get('CompanyName') or 'Unknown Customer',
                    'email': qb_customer.get('PrimaryEmailAddr', {}).get('Address', '') or qb_customer.get('EmailAddr', {}).get('Address', ''),
                    'phone': qb_customer.get('PrimaryPhone', {}).get('FreeFormNumber', '') or qb_customer.get('Phone', {}).get('FreeFormNumber', ''),
                    'quickbooks_id': qb_customer.get('Id', ''),
                    'bill_to_name': qb_customer.get('BillAddr', {}).get('Name', ''),
                    'bill_to_address1': qb_customer.get('BillAddr', {}).get('Line1', ''),
                    'bill_to_address2': qb_customer.get('BillAddr', {}).get('Line2', ''),
                    'bill_to_city': qb_customer.get('BillAddr', {}).get('City', ''),
                    'bill_to_state': qb_customer.get('BillAddr', {}).get('CountrySubDivisionCode', ''),
                    'bill_to_zip': qb_customer.get('BillAddr', {}).get('PostalCode', ''),
                    'bill_to_country': qb_customer.get('BillAddr', {}).get('Country', 'USA'),
                    'ship_to_name': qb_customer.get('ShipAddr', {}).get('Name', ''),
                    'ship_to_address1': qb_customer.get('ShipAddr', {}).get('Line1', ''),
                    'ship_to_address2': qb_customer.get('ShipAddr', {}).get('Line2', ''),
                    'ship_to_city': qb_customer.get('ShipAddr', {}).get('City', ''),
                    'ship_to_state': qb_customer.get('ShipAddr', {}).get('CountrySubDivisionCode', ''),
                    'ship_to_zip': qb_customer.get('ShipAddr', {}).get('PostalCode', ''),
                    'ship_to_country': qb_customer.get('ShipAddr', {}).get('Country', 'USA'),
                    'payment_terms': qb_customer.get('PaymentMethodRef', {}).get('name', ''),
                    'notes': f"Imported from QuickBooks on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
                
                # Check if customer already exists
                existing_customer = Customer.query.filter_by(quickbooks_id=customer_data['quickbooks_id']).first()
                
                if existing_customer:
                    # Update existing customer
                    for key, value in customer_data.items():
                        if hasattr(existing_customer, key) and value:
                            setattr(existing_customer, key, value)
                    customers_updated += 1
                else:
                    # Create new customer
                    customer = Customer(**customer_data)
                    db.session.add(customer)
                    customers_imported += 1
                    
            except Exception as e:
                errors.append(f"Error processing customer {qb_customer.get('Name', 'Unknown')}: {str(e)}")
        
        db.session.commit()
        clear_cache()
        
        return {
            'success': True,
            'customers_imported': customers_imported,
            'customers_updated': customers_updated,
            'errors': errors
        }
        
    except Exception as e:
        db.session.rollback()
        return {'error': f'Import failed: {str(e)}'}

def import_qb_items():
    """Import items from QuickBooks"""
    try:
        # Get items from QuickBooks using query endpoint
        query = "SELECT * FROM Item WHERE Type = 'Inventory'"
        result = make_qb_api_request(f'query?query={query}&minorversion=75')
        if 'error' in result:
            return result
        
        items_imported = 0
        items_updated = 0
        errors = []
        
        for qb_item in result.get('QueryResponse', {}).get('Item', []):
            try:
                # Skip service items, only import inventory items
                if qb_item.get('Type') != 'Inventory':
                    continue
                
                # Extract item data from QB response with fallbacks
                item_data = {
                    'name': qb_item.get('Name') or qb_item.get('DisplayName') or 'Unknown Item',
                    'item_code': qb_item.get('Sku', '') or f"QB-{qb_item.get('Id', '')}",
                    'gtin': qb_item.get('UPC', '') or f"QB{qb_item.get('Id', '').zfill(13)}",
                    'category': qb_item.get('ItemCategoryRef', {}).get('name', 'Imported'),
                    'description': qb_item.get('Description', '') or f"Imported from QuickBooks on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
                
                # Check if item already exists
                existing_item = Item.query.filter_by(item_code=item_data['item_code']).first()
                
                if existing_item:
                    # Update existing item
                    for key, value in item_data.items():
                        if hasattr(existing_item, key) and value:
                            setattr(existing_item, key, value)
                    items_updated += 1
                else:
                    # Create new item
                    item = Item(**item_data)
                    db.session.add(item)
                    items_imported += 1
                    
            except Exception as e:
                errors.append(f"Error processing item {qb_item.get('Name', 'Unknown')}: {str(e)}")
        
        db.session.commit()
        clear_cache()
        
        return {
            'success': True,
            'items_imported': items_imported,
            'items_updated': items_updated,
            'errors': errors
        }
        
    except Exception as e:
        db.session.rollback()
        return {'error': f'Import failed: {str(e)}'}

def save_receiving_photo(file, lot_code):
    """Save receiving photo and return the file path"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(f"{lot_code}_{uuid.uuid4().hex[:8]}.{file.filename.rsplit('.', 1)[1].lower()}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(filepath)
        
        # Resize image if too large (max 1920x1080)
        try:
            with Image.open(filepath) as img:
                if img.width > 1920 or img.height > 1080:
                    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                    img.save(filepath, optimize=True, quality=85)
        except Exception as e:
            print(f"Error resizing image: {e}")
        
        return filename
    return None

def track_user_session():
    """Track active user sessions"""
    if session.get('admin_logged_in'):
        user_id = session.get('admin_id')
        user_email = session.get('admin_email')
        
        with session_lock:
            active_sessions[user_id] = {
                'email': user_email,
                'last_activity': time.time(),
                'ip_address': request.remote_addr
            }
            
            # Clean old sessions (older than 1 hour)
            current_time = time.time()
            expired_sessions = [uid for uid, data in active_sessions.items() 
                              if current_time - data['last_activity'] > 3600]
            for uid in expired_sessions:
                del active_sessions[uid]

# Database Models
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    item_code = db.Column(db.String(20), unique=True, nullable=False, index=True)  # Numerical item code
    gtin = db.Column(db.String(14), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), index=True)  # New field for item categorization
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    lots = db.relationship('Lot', backref='item', lazy=True)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    contact_person = db.Column(db.String(100), index=True)
    email = db.Column(db.String(100), index=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    lots = db.relationship('Lot', backref='vendor', lazy=True)

class Lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False, index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=True, index=True)  # New field for vendor tracking
    quantity = db.Column(db.Integer, default=0, index=True)
    unit_type = db.Column(db.String(20), default='cases', index=True)  # cases or pounds
    expiry_date = db.Column(db.Date, default=lambda: (datetime.now(timezone.utc) + timedelta(days=10)).date(), index=True)  # Auto 10 days
    receiving_date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date(), index=True)  # New field for receiving date
    notes = db.Column(db.Text)  # New field for LOT notes
    photo_path = db.Column(db.String(255), nullable=True)  # Path to receiving photo
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    status = db.Column(db.String(20), default='active', index=True)  # active, expired, consumed

# Admin User Model
class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(50), nullable=False, index=True)
    last_name = db.Column(db.String(50), nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_super_admin = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    last_login = db.Column(db.DateTime, index=True)
    password_reset_token = db.Column(db.String(100), nullable=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)

class PrintJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_code = db.Column(db.String(50), nullable=False)
    printer_id = db.Column(db.Integer, db.ForeignKey('printer.id'), nullable=False)
    template = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='pending')  # pending, printing, completed, failed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=True)
    
    # Relationships
    printer = db.relationship('Printer', backref='print_jobs')
    user = db.relationship('AdminUser', backref='print_jobs')

# Printer Configuration Model
class Printer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    ip_address = db.Column(db.String(15), nullable=False, index=True)
    port = db.Column(db.Integer, default=9100)
    printer_type = db.Column(db.String(50), default='zebra', index=True)
    label_width = db.Column(db.Float, default=4.0)
    label_height = db.Column(db.Float, default=2.0)
    dpi = db.Column(db.Integer, default=203)
    status = db.Column(db.String(20), default='offline', index=True)
    last_seen = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True, index=True)
    phone = db.Column(db.String(20), nullable=True)
    quickbooks_id = db.Column(db.String(100), nullable=True, index=True)  # QB Customer ID
    
    # Billing Address
    bill_to_name = db.Column(db.String(200), nullable=True)
    bill_to_address1 = db.Column(db.String(200), nullable=True)
    bill_to_address2 = db.Column(db.String(200), nullable=True)
    bill_to_city = db.Column(db.String(100), nullable=True)
    bill_to_state = db.Column(db.String(50), nullable=True)
    bill_to_zip = db.Column(db.String(20), nullable=True)
    bill_to_country = db.Column(db.String(100), default='USA')
    
    # Shipping Address
    ship_to_name = db.Column(db.String(200), nullable=True)
    ship_to_address1 = db.Column(db.String(200), nullable=True)
    ship_to_address2 = db.Column(db.String(200), nullable=True)
    ship_to_city = db.Column(db.String(100), nullable=True)
    ship_to_state = db.Column(db.String(50), nullable=True)
    ship_to_zip = db.Column(db.String(20), nullable=True)
    ship_to_country = db.Column(db.String(100), default='USA')
    
    # Additional fields
    tax_id = db.Column(db.String(50), nullable=True)
    payment_terms = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), nullable=False, unique=True, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False, index=True)
    
    # Order details
    order_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    requested_delivery_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='pending', index=True)  # pending, in_progress, filled, shipped, completed, cancelled
    
    # QuickBooks integration
    quickbooks_id = db.Column(db.String(100), nullable=True, index=True)  # QB Sales Receipt ID
    quickbooks_synced = db.Column(db.Boolean, default=False, index=True)
    quickbooks_sync_date = db.Column(db.DateTime, nullable=True)
    
    # Order totals
    subtotal = db.Column(db.Numeric(10, 2), default=0)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    
    # Additional fields
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False, index=True)
    
    # Order item details
    quantity_ordered = db.Column(db.Numeric(10, 2), nullable=False)
    quantity_filled = db.Column(db.Numeric(10, 2), default=0)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Lot tracking
    lots_used = db.Column(db.Text, nullable=True)  # JSON string of lot allocations
    
    # Status
    status = db.Column(db.String(50), default='pending', index=True)  # pending, partial, filled
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    item = db.relationship('Item', backref='order_items')

class LotAllocation(db.Model):
    """Tracks which lots are allocated to specific order items"""
    id = db.Column(db.Integer, primary_key=True)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_item.id'), nullable=False, index=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('lot.id'), nullable=False, index=True)
    quantity_allocated = db.Column(db.Numeric(10, 2), nullable=False)
    allocated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    allocated_by = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=True)
    
    # Relationships
    order_item = db.relationship('OrderItem', backref='lot_allocations')
    lot = db.relationship('Lot', backref='allocations')

# Authentication decorator
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index_new.html')

@app.route('/orders')
@admin_required
def orders():
    """Order management page"""
    return render_template('orders.html')

@app.route('/orders/new')
@admin_required
def new_order():
    """New order entry page"""
    return render_template('order_entry.html')

@app.route('/orders/<int:order_id>/fill')
@admin_required
def fill_order(order_id):
    """Order filling page"""
    return render_template('order_fill.html', order_id=order_id)

@app.route('/customers')
@admin_required
def customers():
    """Customer management page"""
    return render_template('customers.html')

@app.route('/quickbooks-import')
@admin_required
def quickbooks_import():
    """QuickBooks import page"""
    return render_template('quickbooks_import.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        admin = AdminUser.query.filter_by(email=email, is_active=True).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_logged_in'] = True
            session['admin_email'] = admin.email
            session['admin_name'] = f"{admin.first_name} {admin.last_name}"
            session['admin_id'] = admin.id
            session['is_super_admin'] = admin.is_super_admin
            admin.last_login = datetime.now(timezone.utc)
            db.session.commit()
            flash('Login successful!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_email', None)
    session.pop('admin_name', None)
    session.pop('admin_id', None)
    session.pop('is_super_admin', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('admin_login'))

# Admin User Management Routes
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_admin_users():
    """Get all admin users (super admin only)"""
    if not session.get('is_super_admin'):
        return jsonify({'error': 'Access denied. Super admin required.'}), 403
    
    users = AdminUser.query.all()
    return jsonify([{
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'is_super_admin': user.is_super_admin,
        'created_at': user.created_at.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None
    } for user in users])

@app.route('/api/admin/users', methods=['POST'])
@admin_required
def create_admin_user():
    """Create a new admin user (super admin only)"""
    if not session.get('is_super_admin'):
        return jsonify({'error': 'Access denied. Super admin required.'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if email already exists
    existing_user = AdminUser.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'Email already exists'}), 400
    
    try:
        user = AdminUser(
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            is_super_admin=data.get('is_super_admin', False)
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Admin user created successfully',
            'user_id': user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_admin_user(user_id):
    """Update an admin user (super admin only)"""
    if not session.get('is_super_admin'):
        return jsonify({'error': 'Access denied. Super admin required.'}), 403
    
    user = AdminUser.query.get_or_404(user_id)
    data = request.get_json()
    
    try:
        if 'email' in data:
            # Check if email already exists for another user
            existing_user = AdminUser.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Email already exists'}), 400
            user.email = data['email']
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        if 'is_super_admin' in data:
            user.is_super_admin = data['is_super_admin']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Admin user updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_admin_user(user_id):
    """Delete an admin user (super admin only)"""
    if not session.get('is_super_admin'):
        return jsonify({'error': 'Access denied. Super admin required.'}), 403
    
    # Prevent deleting yourself
    if user_id == session.get('admin_id'):
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    user = AdminUser.query.get_or_404(user_id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Admin user deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_admin_password(user_id):
    """Reset an admin user's password (super admin only)"""
    if not session.get('is_super_admin'):
        return jsonify({'error': 'Access denied. Super admin required.'}), 403
    
    user = AdminUser.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data.get('new_password'):
        return jsonify({'error': 'New password is required'}), 400
    
    try:
        user.password_hash = generate_password_hash(data['new_password'])
        user.password_reset_token = None
        user.password_reset_expires = None
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password reset successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/admin')
@admin_required
def admin():
    return render_template('admin_new.html')

@app.route('/label-designer')
@admin_required
def label_designer():
    return render_template('label_designer_new.html')

@app.route('/receiving')
def receiving():
    return render_template('receiving_new.html')

@app.route('/api/items', methods=['GET'])
def get_items():
    # Check cache first
    cached_items = get_from_cache('items')
    if cached_items is not None:
        return jsonify(cached_items)
    
    # Query database with optimization
    items = Item.query.options(db.joinedload(Item.lots)).all()
    items_data = [{
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'item_code': item.item_code,
        'gtin': item.gtin,
        'category': item.category,
        'created_at': item.created_at.isoformat(),
        'lot_count': len(item.lots)
    } for item in items]
    
    # Cache the result
    set_cache('items', items_data)
    return jsonify(items_data)

@app.route('/api/items', methods=['POST'])
@admin_required
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
        
        # Clear cache when data changes
        clear_cache()
        
        return jsonify({'success': True, 'id': item.id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/lots', methods=['GET'])
def get_lots():
    lots = Lot.query.all()
    return jsonify([{
        'id': lot.id,
        'lot_code': lot.lot_code,
        'item': {
            'id': lot.item.id if lot.item else None,
            'name': lot.item.name if lot.item else 'Unknown Item',
            'item_code': lot.item.item_code if lot.item else 'N/A',
            'gtin': lot.item.gtin if lot.item else None
        },
        'item_name': lot.item.name if lot.item else 'Unknown Item',
        'item_code': lot.item.item_code if lot.item else 'N/A',
        'item_gtin': lot.item.gtin if lot.item else None,
        'quantity': lot.quantity,
        'unit_type': lot.unit_type,
        'expiry_date': lot.expiry_date.isoformat() if lot.expiry_date else None,
        'receiving_date': lot.receiving_date.isoformat() if lot.receiving_date else None,
        'vendor': {
            'id': lot.vendor.id if lot.vendor else None,
            'name': lot.vendor.name if lot.vendor else None
        },
        'vendor_name': lot.vendor.name if lot.vendor else None,
        'vendor_id': lot.vendor_id,
        'notes': lot.notes,
        'photo_path': lot.photo_path,
        'photo_url': f'/uploads/{lot.photo_path}' if lot.photo_path else None,
        'created_at': lot.created_at.isoformat(),
        'status': lot.status
    } for lot in lots])

@app.route('/api/lots', methods=['POST'])
@admin_required
def create_lot():
    data = request.json
    try:
        # Generate unique LOT code
        lot_code = generate_lot_code(data['item_id'])
        
        # Auto-set expiry date to 10 days from today for admin-created lots
        auto_expiry_date = (datetime.now(timezone.utc) + timedelta(days=10)).date()
        
        lot = Lot(
            lot_code=lot_code,
            item_id=data['item_id'],
            quantity=data.get('quantity', 0),
            expiry_date=auto_expiry_date,  # Always auto-set to 10 days from today
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
@rate_limit(max_requests=20, window=60)  # 20 print requests per minute
def print_label_direct(lot_code):
    """Print label directly to printer via IP"""
    data = request.json
    printer_id = data.get('printer_id')
    template = data.get('template', 'palumbo')
    quantity = data.get('quantity', 1)
    
    if not printer_id:
        return jsonify({'error': 'Printer ID required'}), 400
    
    printer = db.session.get(Printer, printer_id)
    if not printer:
        return jsonify({'error': 'Printer not found'}), 404
    
    lot = Lot.query.filter_by(lot_code=lot_code).first()
    if not lot:
        return jsonify({'error': 'Lot not found'}), 404
    
    try:
        # Track user session
        track_user_session()
        
        # Use print queue lock to prevent conflicts
        with print_queue_lock:
            # Create print job record
            user_id = session.get('admin_id') if session.get('admin_logged_in') else None
            print_job = PrintJob(
                lot_code=lot_code,
                printer_id=printer_id,
                template=template,
                quantity=quantity,
                status='printing',
                started_at=datetime.now(timezone.utc),
                user_id=user_id
            )
            db.session.add(print_job)
            db.session.commit()
        
        # Generate ZPL based on template
        if template == 'pti':
            zpl_code = generate_pti_zpl(lot)
        elif template == 'pti-voice-pick':
            zpl_code = generate_pti_voice_pick_zpl(lot)
        else:
            zpl_code = generate_palumbo_zpl(lot)
        
        # Send multiple copies to printer
        success_count = 0
        for i in range(quantity):
            success = send_zpl_to_printer(printer, zpl_code)
            if success:
                success_count += 1
        
        # Update print job status
        if success_count == quantity:
            print_job.status = 'completed'
            print_job.completed_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'{quantity} label(s) sent to {printer.name} ({printer.ip_address})',
                'printer': printer.name,
                'ip': printer.ip_address,
                'quantity': quantity,
                'job_id': print_job.id
            })
        elif success_count > 0:
            print_job.status = 'completed'
            print_job.completed_at = datetime.now(timezone.utc)
            print_job.error_message = f'{quantity - success_count} labels failed to print'
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'{success_count} of {quantity} label(s) sent to {printer.name}',
                'printer': printer.name,
                'ip': printer.ip_address,
                'quantity': success_count,
                'warning': f'{quantity - success_count} labels failed to print',
                'job_id': print_job.id
            })
        else:
            print_job.status = 'failed'
            print_job.completed_at = datetime.now(timezone.utc)
            print_job.error_message = 'Failed to send any labels to printer'
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': f'Failed to send any labels to printer {printer.name}',
                'job_id': print_job.id
            }), 500
            
    except Exception as e:
        # Update print job status if it was created
        if 'print_job' in locals():
            print_job.status = 'failed'
            print_job.completed_at = datetime.now(timezone.utc)
            print_job.error_message = str(e)
            db.session.commit()
        
        return jsonify({'success': False, 'error': str(e)}), 500

# Label preview endpoint
@app.route('/api/lots/<lot_code>/label/<template>/preview', methods=['GET'])
def preview_label(lot_code, template):
    """Preview label content without printing"""
    try:
        lot = Lot.query.filter_by(lot_code=lot_code).first()
        if not lot:
            return jsonify({'error': 'Lot not found'}), 404
        
        # Generate ZPL based on template
        if template == 'pti':
            zpl_code = generate_pti_zpl(lot)
        elif template == 'pti-voice-pick':
            zpl_code = generate_pti_voice_pick_zpl(lot)
        else:
            zpl_code = generate_palumbo_zpl(lot)
        
        # Create a human-readable preview
        preview_text = create_label_preview(lot, template, zpl_code)
        
        return jsonify({
            'success': True,
            'preview_text': preview_text,
            'zpl_code': zpl_code,
            'template': template,
            'lot_code': lot_code
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def create_label_preview(lot, template, zpl_code):
    """Create a human-readable preview of the label"""
    preview = f"""
LOT Code: {lot.lot_code}
Item: {lot.item.name}
Item Code: {lot.item.item_code}
GTIN: {lot.item.gtin}
Quantity: {lot.quantity} {lot.unit_type}
Expiry Date: {lot.expiry_date.strftime('%Y-%m-%d') if lot.expiry_date else 'Not set'}
Vendor: {lot.vendor.name if lot.vendor else 'Not specified'}
Receiving Date: {lot.receiving_date.strftime('%Y-%m-%d') if lot.receiving_date else 'Not specified'}

Template: {template.upper()}
Label Size: 4" x 2"

ZPL Code Preview:
{zpl_code[:500]}{'...' if len(zpl_code) > 500 else ''}
    """.strip()
    
    return preview

# Batch print endpoint for multiple lots
@app.route('/api/lots/batch/print', methods=['POST'])
@rate_limit(max_requests=10, window=60)  # 10 batch requests per minute
def batch_print_labels():
    """Print multiple lots to a single printer"""
    data = request.json
    lot_codes = data.get('lot_codes', [])
    printer_id = data.get('printer_id')
    template = data.get('template', 'palumbo')
    quantity = data.get('quantity', 1)
    
    if not lot_codes:
        return jsonify({'error': 'No LOT codes provided'}), 400
    
    if not printer_id:
        return jsonify({'error': 'Printer ID required'}), 400
    
    printer = db.session.get(Printer, printer_id)
    if not printer:
        return jsonify({'error': 'Printer not found'}), 404
    
    # Track user session
    track_user_session()
    
    results = []
    total_success = 0
    total_failed = 0
    
    # Use print queue lock for batch operations
    with print_queue_lock:
        for lot_code in lot_codes:
            lot = Lot.query.filter_by(lot_code=lot_code).first()
            if not lot:
                results.append({
                    'lot_code': lot_code,
                    'success': False,
                    'error': 'Lot not found'
                })
                total_failed += 1
                continue
            
            try:
                # Generate ZPL based on template
                if template == 'pti':
                    zpl_code = generate_pti_zpl(lot)
                elif template == 'pti-voice-pick':
                    zpl_code = generate_pti_voice_pick_zpl(lot)
                else:
                    zpl_code = generate_palumbo_zpl(lot)
                
                # Send multiple copies to printer
                success_count = 0
                for i in range(quantity):
                    success = send_zpl_to_printer(printer, zpl_code)
                    if success:
                        success_count += 1
                
                if success_count == quantity:
                    results.append({
                        'lot_code': lot_code,
                        'success': True,
                        'quantity': quantity,
                        'message': f'{quantity} label(s) printed successfully'
                    })
                    total_success += 1
                elif success_count > 0:
                    results.append({
                        'lot_code': lot_code,
                        'success': True,
                        'quantity': success_count,
                        'warning': f'{quantity - success_count} labels failed to print'
                    })
                    total_success += 1
                else:
                    results.append({
                        'lot_code': lot_code,
                        'success': False,
                        'error': 'Failed to print any labels'
                    })
                    total_failed += 1
                    
            except Exception as e:
                results.append({
                    'lot_code': lot_code,
                    'success': False,
                    'error': str(e)
                })
                total_failed += 1
    
    return jsonify({
        'success': total_failed == 0,
        'total_lots': len(lot_codes),
        'successful': total_success,
        'failed': total_failed,
        'printer': printer.name,
        'template': template,
        'quantity_per_lot': quantity,
        'results': results
    })

# Custom Label Generation Endpoint
@app.route('/api/custom-label/generate', methods=['POST'])
@admin_required
def generate_custom_label():
    """Generate a custom label with dynamic dates and barcode"""
    data = request.json
    product_name = data.get('product_name', 'Custom Product')
    item_code = data.get('item_code', 'CUSTOM001')
    pack_date = data.get('pack_date')  # Format: YYYY-MM-DD
    use_by_date = data.get('use_by_date')  # Format: YYYY-MM-DD
    net_weight = data.get('net_weight', '10lbs / 4.5kg')
    gross_weight = data.get('gross_weight', '12lbs / 5.4kgs')
    ingredients = data.get('ingredients', 'Custom Ingredients')
    manufacturer = data.get('manufacturer', 'Palumbo Foods, LLC')
    manufacturer_address = data.get('manufacturer_address', 'Louisville, KY 40299, USA')
    
    # If no dates provided, use current date and 10 days later
    if not pack_date:
        pack_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    if not use_by_date:
        pack_dt = datetime.strptime(pack_date, '%Y-%m-%d')
        use_by_dt = pack_dt + timedelta(days=10)
        use_by_date = use_by_dt.strftime('%Y-%m-%d')
    
    # Format dates for display (MM/DD/YY)
    pack_display = datetime.strptime(pack_date, '%Y-%m-%d').strftime('%m/%d/%y')
    use_by_display = datetime.strptime(use_by_date, '%Y-%m-%d').strftime('%m/%d/%Y')
    
    # Generate barcode data (GTIN + LOT + Use By Date)
    # Using a simple GTIN format: 00850018478243 + item code + use by date (MMDDYY)
    use_by_barcode = datetime.strptime(use_by_date, '%Y-%m-%d').strftime('%m%d%y')
    barcode_data = f"(01)00850018478243(10){item_code}(15){use_by_barcode}"
    
    # Alternative simpler barcode for testing
    simple_barcode = f"00850018478243{item_code}{use_by_barcode}"
    
    # Generate ZPL for custom label using user's exact format
    # Fixed item code 1051, only lot code and dates are dynamic
    zpl_code = f"""CT~~CD,~CC^~CT~
^XA
^MTD
~SD30
^CI27
^XZ
^XA
^MMT
^FT39,57^A0N,28,28^FH\\^CI28^FDPJ Item # 1051^FS^CI27
^FT39,92^A0N,28,28^FH\\^CI28^FDSC - 001219^FS^CI27
^FT336,167^A0N,28,30^FH\\^CI28^FDProduct of USA^FS^CI27
^FT216,100^A0N,28,30^FH\\^CI28^FD{product_name}^FS^CI27
^FT51,230^A0N,23,23^FH\\^CI28^FDPack Date: ^FS^CI27
^FT51,263^A0N,27,28^FH\\^CI28^FDUse By Date:^FS^CI27
^FT577,57^A0N,28,28^FH\\^CI28^FDKeep Refrigerated^FS^CI27
^FT32,216^A0N,17,18^FB798,1,4,C^FH\\^CI28^FDManufactured For: \\5C&^FS^CI27
^FT32,237^A0N,17,18^FB798,1,4,C^FH\\^CI28^FD{manufacturer}\\5C&^FS^CI27
^FT32,258^A0N,17,18^FB798,1,4,C^FH\\^CI28^FD{manufacturer_address}\\5C&^FS^CI27
^FT530,222^A0N,23,23^FH\\^CI28^FDNet Weight: {net_weight}^FS^CI27
^FT530,243^A0N,23,23^FH\\^CI28^FDGross Weight: {gross_weight}^FS^CI27
^FT301,404^A0N,25,28^FH\\^CI28^FDNOT FOR RETAIL SALE^FS^CI27
^FT357,135^A0N,28,28^FH\\^CI28^FD(2) 5lb Tubs^FS^CI27
^FT73,284^A0N,14,15^FH\\^CI28^FDDate Format: MM/DD/YYYY^FS^CI27
^FT573,275^A0N,23,23^FH\\^CI28^FDIngredients: {ingredients}^FS^CI27
^BY1,3,71^FT306,346^BCN,,N,N
^FH\\^FD>;>80100850018478243{item_code}>60>5>8{use_by_barcode}^FS
^FT203,263^A0N,27,28^FH\\^CI28^FD{use_by_display}^FS^CI27
^FT160,231^A0N,23,23^FH\\^CI28^FD{pack_display}^FS^CI27
^FT263,378^A0N,20,20^FH\\^CI28^FD(01)00850018478243(10){item_code}(15){use_by_barcode}^FS^CI27
^XZ"""
    
    return jsonify({
        'success': True,
        'zpl_code': zpl_code,
        'pack_date': pack_date,
        'use_by_date': use_by_date,
        'barcode_data': barcode_data,
        'simple_barcode': simple_barcode
    })

# Test Print Endpoint
@app.route('/api/test-print', methods=['POST'])
@admin_required
def test_print():
    """Test print ZPL code to a printer"""
    data = request.json
    printer_id = data.get('printer_id')
    zpl_code = data.get('zpl_code')
    
    if not printer_id or not zpl_code:
        return jsonify({'error': 'Printer ID and ZPL code are required'}), 400
    
    printer = db.session.get(Printer, printer_id)
    if not printer:
        return jsonify({'error': 'Printer not found'}), 404
    
    try:
        # Track user session
        track_user_session()
        
        # Send ZPL to printer
        success = send_zpl_to_printer(printer, zpl_code)
        
        if success:
            return jsonify({'success': True, 'message': 'Test print sent successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send test print to printer'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Print Queue Management Endpoints
# Active users endpoint
@app.route('/api/active-users', methods=['GET'])
@admin_required
def get_active_users():
    """Get information about currently active users"""
    try:
        with session_lock:
            current_time = time.time()
            active_users = []
            
            for user_id, data in active_sessions.items():
                # Only include sessions active in last 10 minutes
                if current_time - data['last_activity'] < 600:
                    active_users.append({
                        'user_id': user_id,
                        'email': data['email'],
                        'ip_address': data['ip_address'],
                        'last_activity': data['last_activity'],
                        'minutes_ago': int((current_time - data['last_activity']) / 60)
                    })
            
            return jsonify({
                'success': True,
                'active_users': active_users,
                'total_active': len(active_users)
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded photos"""
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/api/print-queue', methods=['GET'])
@rate_limit(max_requests=30, window=60)  # 30 requests per minute
def get_print_queue():
    """Get current print queue status"""
    try:
        jobs = PrintJob.query.order_by(PrintJob.created_at.desc()).limit(50).all()
        
        queue_data = []
        for job in jobs:
            queue_data.append({
                'id': job.id,
                'lot_code': job.lot_code,
                'printer_name': job.printer.name,
                'template': job.template,
                'quantity': job.quantity,
                'status': job.status,
                'created_at': job.created_at.isoformat(),
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'error_message': job.error_message,
                'user_name': f"{job.user.first_name} {job.user.last_name}" if job.user else None
            })
        
        # Get queue statistics
        stats = {
            'pending': PrintJob.query.filter_by(status='pending').count(),
            'printing': PrintJob.query.filter_by(status='printing').count(),
            'completed_today': PrintJob.query.filter(
                PrintJob.status == 'completed',
                PrintJob.completed_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            ).count(),
            'failed_today': PrintJob.query.filter(
                PrintJob.status == 'failed',
                PrintJob.created_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            ).count()
        }
        
        return jsonify({
            'success': True,
            'jobs': queue_data,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/print-queue/<int:job_id>/cancel', methods=['POST'])
def cancel_print_job(job_id):
    """Cancel a pending print job"""
    try:
        job = PrintJob.query.get(job_id)
        if not job:
            return jsonify({'error': 'Print job not found'}), 404
        
        if job.status not in ['pending', 'printing']:
            return jsonify({'error': 'Cannot cancel completed or failed job'}), 400
        
        job.status = 'failed'
        job.error_message = 'Cancelled by user'
        job.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Print job cancelled successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/print-queue/clear-completed', methods=['POST'])
def clear_completed_jobs():
    """Clear completed and failed print jobs older than 24 hours"""
    try:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        deleted_count = PrintJob.query.filter(
            PrintJob.status.in_(['completed', 'failed']),
            PrintJob.completed_at < cutoff_time
        ).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} old print jobs'
        })
        
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
def update_lot(lot_code):
    lot = Lot.query.filter_by(lot_code=lot_code).first_or_404()
    data = request.get_json()
    
    if 'item_id' in data:
        lot.item_id = data['item_id']
    if 'quantity' in data:
        lot.quantity = data['quantity']
    # Always auto-set expiry date to 10 days from today when updating through admin
    auto_expiry_date = (datetime.now(timezone.utc) + timedelta(days=10)).date()
    lot.expiry_date = auto_expiry_date
    if 'notes' in data:
        lot.notes = data['notes']
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'LOT code updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/lots/<lot_code>', methods=['DELETE'])
@admin_required
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
    # Check cache first
    cached_vendors = get_from_cache('vendors')
    if cached_vendors is not None:
        return jsonify(cached_vendors)
    
    # Query database
    vendors = Vendor.query.all()
    vendors_data = [{
        'id': vendor.id,
        'name': vendor.name,
        'contact_person': vendor.contact_person,
        'email': vendor.email,
        'phone': vendor.phone,
        'address': vendor.address,
        'created_at': vendor.created_at.isoformat() if vendor.created_at else None
    } for vendor in vendors]
    
    # Cache the result
    set_cache('vendors', vendors_data)
    return jsonify(vendors_data)

@app.route('/api/vendors', methods=['POST'])
@admin_required
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
    
    # Clear cache when data changes
    clear_cache()
    
    return jsonify({'id': vendor.id, 'message': 'Vendor created successfully'}), 201

@app.route('/api/vendors/<int:vendor_id>', methods=['PUT'])
@admin_required
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
@admin_required
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
    # Handle both JSON and form data (for file uploads)
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Handle form data with file upload
        item_code = request.form.get('item_code')
        quantity = int(request.form.get('quantity', 0))
        vendor_id = int(request.form.get('vendor_id', 0))
        unit_type = request.form.get('unit_type', 'cases')
        notes = request.form.get('notes', '')
        photo = request.files.get('photo')
    else:
        # Handle JSON data
        data = request.get_json()
        item_code = data.get('item_code')
        quantity = data.get('quantity')
        vendor_id = data.get('vendor_id')
        unit_type = data.get('unit_type', 'cases')
        notes = data.get('notes', '')
        photo = None
    
    # Validate required fields
    if not all([item_code, quantity, vendor_id]):
        return jsonify({'error': 'Missing required fields: item_code, quantity, vendor_id'}), 400
    
    # Validate unit_type
    if unit_type not in ['cases', 'pounds']:
        return jsonify({'error': 'unit_type must be either "cases" or "pounds"'}), 400
    
    # Find the item by item_code
    item = Item.query.filter_by(item_code=item_code).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    # Find the vendor
    vendor = db.session.get(Vendor, vendor_id)
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404
    
    # Generate lot code
    lot_code = generate_lot_code(item.id)
    
    # Handle photo upload
    photo_path = None
    if photo:
        photo_path = save_receiving_photo(photo, lot_code)
    
    # Create the lot
    lot = Lot(
        lot_code=lot_code,
        item_id=item.id,
        vendor_id=vendor.id,
        quantity=quantity,
        unit_type=unit_type,
        receiving_date=datetime.now(timezone.utc).date(),
        notes=notes,
        photo_path=photo_path
    )
    
    db.session.add(lot)
    db.session.commit()
    
    return jsonify({
        'lot_id': lot.id,
        'lot_code': lot.lot_code,
        'item_name': item.name,
        'vendor_name': vendor.name,
        'quantity': lot.quantity,
        'unit_type': lot.unit_type,
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
            
            # Validate unit_type
            unit_type = item_data.get('unit_type', 'cases')
            if unit_type not in ['cases', 'pounds']:
                errors.append(f"Invalid unit_type for item {item_data['item_code']}: must be 'cases' or 'pounds'")
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
                unit_type=unit_type,
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
                'unit_type': lot.unit_type,
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
    p.drawString(470, y_position, "Unit")
    p.drawString(510, y_position, "Expiry Date")
    
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
        p.drawString(470, y_position, lot.unit_type)
        p.drawString(510, y_position, lot.expiry_date.strftime('%Y-%m-%d'))
        
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

# =============================================================================
# ORDER SYSTEM API ENDPOINTS
# =============================================================================

@app.route('/api/customers', methods=['GET'])
@admin_required
def get_customers():
    """Get all customers"""
    try:
        customers = Customer.query.filter_by(is_active=True).all()
        return jsonify([{
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'quickbooks_id': customer.quickbooks_id,
            'bill_to_name': customer.bill_to_name,
            'bill_to_address1': customer.bill_to_address1,
            'bill_to_city': customer.bill_to_city,
            'bill_to_state': customer.bill_to_state,
            'bill_to_zip': customer.bill_to_zip,
            'ship_to_name': customer.ship_to_name,
            'ship_to_address1': customer.ship_to_address1,
            'ship_to_city': customer.ship_to_city,
            'ship_to_state': customer.ship_to_state,
            'ship_to_zip': customer.ship_to_zip,
            'payment_terms': customer.payment_terms,
            'notes': customer.notes,
            'created_at': customer.created_at.isoformat() if customer.created_at else None
        } for customer in customers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers', methods=['POST'])
@admin_required
def create_customer():
    """Create a new customer"""
    try:
        data = request.get_json()
        
        customer = Customer(
            name=data['name'],
            email=data.get('email'),
            phone=data.get('phone'),
            quickbooks_id=data.get('quickbooks_id'),
            bill_to_name=data.get('bill_to_name'),
            bill_to_address1=data.get('bill_to_address1'),
            bill_to_address2=data.get('bill_to_address2'),
            bill_to_city=data.get('bill_to_city'),
            bill_to_state=data.get('bill_to_state'),
            bill_to_zip=data.get('bill_to_zip'),
            bill_to_country=data.get('bill_to_country', 'USA'),
            ship_to_name=data.get('ship_to_name'),
            ship_to_address1=data.get('ship_to_address1'),
            ship_to_address2=data.get('ship_to_address2'),
            ship_to_city=data.get('ship_to_city'),
            ship_to_state=data.get('ship_to_state'),
            ship_to_zip=data.get('ship_to_zip'),
            ship_to_country=data.get('ship_to_country', 'USA'),
            tax_id=data.get('tax_id'),
            payment_terms=data.get('payment_terms'),
            notes=data.get('notes')
        )
        
        db.session.add(customer)
        db.session.commit()
        clear_cache()
        
        return jsonify({'success': True, 'id': customer.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
@admin_required
def update_customer(customer_id):
    """Update a customer"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        data = request.get_json()
        
        customer.name = data.get('name', customer.name)
        customer.email = data.get('email', customer.email)
        customer.phone = data.get('phone', customer.phone)
        customer.quickbooks_id = data.get('quickbooks_id', customer.quickbooks_id)
        customer.bill_to_name = data.get('bill_to_name', customer.bill_to_name)
        customer.bill_to_address1 = data.get('bill_to_address1', customer.bill_to_address1)
        customer.bill_to_address2 = data.get('bill_to_address2', customer.bill_to_address2)
        customer.bill_to_city = data.get('bill_to_city', customer.bill_to_city)
        customer.bill_to_state = data.get('bill_to_state', customer.bill_to_state)
        customer.bill_to_zip = data.get('bill_to_zip', customer.bill_to_zip)
        customer.bill_to_country = data.get('bill_to_country', customer.bill_to_country)
        customer.ship_to_name = data.get('ship_to_name', customer.ship_to_name)
        customer.ship_to_address1 = data.get('ship_to_address1', customer.ship_to_address1)
        customer.ship_to_address2 = data.get('ship_to_address2', customer.ship_to_address2)
        customer.ship_to_city = data.get('ship_to_city', customer.ship_to_city)
        customer.ship_to_state = data.get('ship_to_state', customer.ship_to_state)
        customer.ship_to_zip = data.get('ship_to_zip', customer.ship_to_zip)
        customer.ship_to_country = data.get('ship_to_country', customer.ship_to_country)
        customer.tax_id = data.get('tax_id', customer.tax_id)
        customer.payment_terms = data.get('payment_terms', customer.payment_terms)
        customer.notes = data.get('notes', customer.notes)
        customer.is_active = data.get('is_active', customer.is_active)
        
        db.session.commit()
        clear_cache()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['GET'])
@admin_required
def get_orders():
    """Get all orders with optional filtering"""
    try:
        status = request.args.get('status')
        customer_id = request.args.get('customer_id')
        
        query = Order.query.options(
            db.joinedload(Order.customer),
            db.joinedload(Order.order_items).joinedload(OrderItem.item)
        )
        
        if status:
            query = query.filter(Order.status == status)
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        
        orders = query.order_by(Order.created_at.desc()).all()
        
        return jsonify([{
            'id': order.id,
            'order_number': order.order_number,
            'customer_id': order.customer_id,
            'customer_name': order.customer.name if order.customer else None,
            'order_date': order.order_date.isoformat() if order.order_date else None,
            'requested_delivery_date': order.requested_delivery_date.isoformat() if order.requested_delivery_date else None,
            'status': order.status,
            'subtotal': float(order.subtotal),
            'tax_amount': float(order.tax_amount),
            'total_amount': float(order.total_amount),
            'quickbooks_synced': order.quickbooks_synced,
            'notes': order.notes,
            'order_items': [{
                'id': item.id,
                'item_id': item.item_id,
                'item_name': item.item.name if item.item else None,
                'quantity_ordered': float(item.quantity_ordered),
                'quantity_filled': float(item.quantity_filled),
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price),
                'status': item.status,
                'notes': item.notes
            } for item in order.order_items],
            'created_at': order.created_at.isoformat() if order.created_at else None
        } for order in orders])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['POST'])
@admin_required
def create_order():
    """Create a new order"""
    try:
        data = request.get_json()
        
        # Generate order number
        order_number = generate_order_number()
        
        # Calculate totals
        totals = calculate_order_totals(data['order_items'])
        
        # Create order
        order = Order(
            order_number=order_number,
            customer_id=data['customer_id'],
            requested_delivery_date=datetime.strptime(data['requested_delivery_date'], '%Y-%m-%d').date() if data.get('requested_delivery_date') else None,
            subtotal=totals['subtotal'],
            tax_amount=totals['tax_amount'],
            total_amount=totals['total_amount'],
            notes=data.get('notes'),
            created_by=session.get('user_id')
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Create order items
        for item_data in data['order_items']:
            order_item = OrderItem(
                order_id=order.id,
                item_id=item_data['item_id'],
                quantity_ordered=item_data['quantity_ordered'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price'],
                notes=item_data.get('notes')
            )
            db.session.add(order_item)
        
        db.session.commit()
        clear_cache()
        
        return jsonify({'success': True, 'id': order.id, 'order_number': order_number}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>/fill', methods=['POST'])
@admin_required
def fill_order_item():
    """Fill an order item with specific lots"""
    try:
        data = request.get_json()
        order_item_id = data['order_item_id']
        lot_allocations = data['lot_allocations']  # [{'lot_id': 1, 'quantity': 10}]
        
        order_item = OrderItem.query.get(order_item_id)
        if not order_item:
            return jsonify({'error': 'Order item not found'}), 404
        
        # Validate total quantity
        total_allocated = sum(allocation['quantity'] for allocation in lot_allocations)
        remaining_quantity = float(order_item.quantity_ordered) - float(order_item.quantity_filled)
        
        if total_allocated > remaining_quantity:
            return jsonify({'error': 'Allocated quantity exceeds remaining quantity'}), 400
        
        # Create lot allocations
        for allocation in lot_allocations:
            lot = Lot.query.get(allocation['lot_id'])
            if not lot:
                return jsonify({'error': f'Lot {allocation["lot_id"]} not found'}), 404
            
            if float(lot.quantity) < allocation['quantity']:
                return jsonify({'error': f'Insufficient quantity in lot {lot.lot_code}'}), 400
            
            lot_allocation = LotAllocation(
                order_item_id=order_item_id,
                lot_id=allocation['lot_id'],
                quantity_allocated=allocation['quantity'],
                allocated_by=session.get('user_id')
            )
            db.session.add(lot_allocation)
            
            # Update lot quantity
            lot.quantity = float(lot.quantity) - allocation['quantity']
        
        # Update order item
        order_item.quantity_filled = float(order_item.quantity_filled) + total_allocated
        if order_item.quantity_filled >= order_item.quantity_ordered:
            order_item.status = 'filled'
        else:
            order_item.status = 'partial'
        
        # Update order status
        order = order_item.order
        all_filled = all(item.status == 'filled' for item in order.order_items)
        if all_filled:
            order.status = 'filled'
        else:
            order.status = 'in_progress'
        
        db.session.commit()
        clear_cache()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>/lots-available', methods=['GET'])
@admin_required
def get_available_lots_for_order():
    """Get available lots for filling an order item"""
    try:
        order_item_id = request.args.get('order_item_id')
        if not order_item_id:
            return jsonify({'error': 'order_item_id is required'}), 400
        
        order_item = OrderItem.query.get(order_item_id)
        if not order_item:
            return jsonify({'error': 'Order item not found'}), 404
        
        # Get lots for this item that have available quantity
        lots = Lot.query.filter(
            Lot.item_id == order_item.item_id,
            Lot.quantity > 0,
            Lot.status == 'available'
        ).all()
        
        return jsonify([{
            'id': lot.id,
            'lot_code': lot.lot_code,
            'quantity': float(lot.quantity),
            'unit_type': lot.unit_type,
            'expiry_date': lot.expiry_date.isoformat() if lot.expiry_date else None,
            'receiving_date': lot.receiving_date.isoformat() if lot.receiving_date else None,
            'vendor_name': lot.vendor.name if lot.vendor else None
        } for lot in lots])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# QuickBooks Integration Endpoints
@app.route('/api/quickbooks/connect', methods=['GET'])
@admin_required
def quickbooks_connect():
    """Initiate QuickBooks OAuth connection"""
    try:
        # Generate state parameter for security
        state = secrets.token_urlsafe(32)
        session['qb_state'] = state
        
        # Build authorization URL
        auth_url = (
            f"https://appcenter.intuit.com/connect/oauth2?"
            f"client_id={QB_CLIENT_ID}&"
            f"scope={QB_SCOPE}&"
            f"redirect_uri={QB_REDIRECT_URI}&"
            f"response_type=code&"
            f"state={state}"
        )
        
        return jsonify({'auth_url': auth_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/qb/callback')
@admin_required
def quickbooks_callback():
    """Handle QuickBooks OAuth callback"""
    try:
        # Get authorization code and state from callback
        code = request.args.get('code')
        state = request.args.get('state')
        realm_id = request.args.get('realmId')  # Company ID
        
        # Verify state parameter
        if state != session.get('qb_state'):
            return jsonify({'error': 'Invalid state parameter'}), 400
        
        if not code:
            return jsonify({'error': 'Authorization code not provided'}), 400
        
        # Exchange authorization code for access token
        token_url = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': QB_REDIRECT_URI
        }
        
        # Make token request
        response = requests.post(token_url, data=token_data, auth=(QB_CLIENT_ID, QB_CLIENT_SECRET))
        
        if response.status_code != 200:
            return jsonify({
                'error': 'Failed to exchange code for token',
                'details': response.text
            }), 400
        
        token_response = response.json()
        
        # Store tokens in session (in production, store securely)
        session['qb_access_token'] = token_response.get('access_token')
        session['qb_refresh_token'] = token_response.get('refresh_token')
        session['qb_company_id'] = realm_id
        
        # Update global company ID
        global QB_COMPANY_ID
        QB_COMPANY_ID = realm_id
        
        return jsonify({
            'success': True,
            'message': 'QuickBooks connected successfully',
            'company_id': realm_id,
            'expires_in': token_response.get('expires_in')
        })
        
    except Exception as e:
        return jsonify({
            'error': 'OAuth callback failed',
            'details': str(e)
        }), 500

@app.route('/api/orders/<int:order_id>/sync-quickbooks', methods=['POST'])
@admin_required
def sync_order_to_quickbooks(order_id):
    """Sync an order to QuickBooks Online"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.quickbooks_synced:
            return jsonify({'error': 'Order already synced to QuickBooks'}), 400
        
        # TODO: Implement actual QuickBooks API integration
        # For now, just mark as synced
        order.quickbooks_synced = True
        order.quickbooks_sync_date = datetime.now(timezone.utc)
        order.quickbooks_id = f"QB-{order.order_number}"
        
        db.session.commit()
        
        return jsonify({'success': True, 'quickbooks_id': order.quickbooks_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/quickbooks/import/customers', methods=['POST'])
@admin_required
def import_quickbooks_customers():
    """Import customers from QuickBooks Online"""
    try:
        result = import_qb_customers()
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify({
            'success': True,
            'message': f"Import completed: {result['customers_imported']} new customers, {result['customers_updated']} updated",
            'customers_imported': result['customers_imported'],
            'customers_updated': result['customers_updated'],
            'errors': result['errors']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quickbooks/import/items', methods=['POST'])
@admin_required
def import_quickbooks_items():
    """Import items from QuickBooks Online"""
    try:
        result = import_qb_items()
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify({
            'success': True,
            'message': f"Import completed: {result['items_imported']} new items, {result['items_updated']} updated",
            'items_imported': result['items_imported'],
            'items_updated': result['items_updated'],
            'errors': result['errors']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quickbooks/test-connection', methods=['GET'])
@admin_required
def test_quickbooks_connection():
    """Test QuickBooks API connection"""
    try:
        # Check if we have an access token
        access_token = get_qb_access_token()
        if not access_token:
            return jsonify({
                'success': False,
                'error': 'No access token found',
                'message': 'Please connect to QuickBooks first using the OAuth flow',
                'action_required': 'oauth_connect',
                'details': {
                    'client_id': QB_CLIENT_ID,
                    'redirect_uri': QB_REDIRECT_URI,
                    'scope': QB_SCOPE
                }
            }), 400
        
        # Test with a simple API call using query endpoint
        query = "SELECT * FROM CompanyInfo"
        result = make_qb_api_request(f'query?query={query}&minorversion=75')
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error'],
                'message': 'QuickBooks API call failed',
                'action_required': 'reconnect' if 'token' in result['error'].lower() else 'check_credentials'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'QuickBooks connection successful',
            'company_info': result.get('QueryResponse', {}).get('CompanyInfo', [{}])[0]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'QuickBooks connection test failed',
            'action_required': 'check_logs'
        }), 500

@app.route('/version')
def get_version():
    """Get application version information"""
    return jsonify({
        'version': VERSION,
        'commit_hash': COMMIT_HASH,
        'branch': BRANCH,
        'build_date': BUILD_DATE,
        'version_info': VERSION_INFO
    })

@app.route('/changelog')
def changelog():
    """Changelog page showing version history"""
    return render_template('changelog.html', 
                         changelog_data=CHANGELOG_DATA,
                         all_versions=get_all_versions(),
                         changelog_summary=get_changelog_summary())

@app.route('/changelog/<version>')
def version_changelog(version):
    """Specific version changelog page"""
    version_data = get_version_changelog(version)
    if not version_data:
        flash(f'Version {version} not found', 'error')
        return redirect(url_for('changelog'))
    
    return render_template('version_changelog.html', 
                         version=version,
                         version_data=version_data,
                         all_versions=get_all_versions())

@app.route('/api/changelog')
def api_changelog():
    """API endpoint for changelog data"""
    return jsonify({
        'changelog': CHANGELOG_DATA,
        'versions': get_all_versions(),
        'summary': get_changelog_summary()
    })

@app.route('/api/changelog/<version>')
def api_version_changelog(version):
    """API endpoint for specific version changelog"""
    version_data = get_version_changelog(version)
    if not version_data:
        return jsonify({'error': 'Version not found'}), 404
    
    return jsonify({
        'version': version,
        'data': version_data
    })

@app.route('/admin/version', methods=['GET', 'POST'])
def admin_version():
    """Admin version management page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        new_version = request.form.get('new_version')
        if new_version:
            try:
                from version import update_manual_version
                result = update_manual_version(new_version)
                if result:
                    flash(f'Version updated to {new_version}', 'success')
                else:
                    flash('Failed to update version', 'error')
            except Exception as e:
                flash(f'Error updating version: {str(e)}', 'error')
        return redirect(url_for('admin_version'))
    
    return render_template('admin_version.html', 
                         version_info=VERSION_INFO,
                         changelog_data=CHANGELOG_DATA)

@app.route('/health')
def health_check():
    """Health check endpoint for load balancers and monitoring"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check Redis connection (if available)
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            redis_status = 'healthy'
        except:
            redis_status = 'unavailable'
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'database': 'connected',
            'redis': redis_status,
            'version': VERSION,
            'commit_hash': COMMIT_HASH
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

if __name__ == '__main__':
    # Initialize database
    with app.app_context():
        db.create_all()
    
    # Production vs Development configuration
    import os
    if os.environ.get('FLASK_ENV') == 'production':
        # Production configuration
        print("🚀 Starting in production mode with Gunicorn...")
        print("Use: gunicorn --config gunicorn.conf.py app:app")
    else:
        # Development configuration
        print("🔧 Starting in development mode...")
        app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG, threaded=True)
