"""
QuickBooks Service

Handles all business logic related to QuickBooks integration including
OAuth authentication, data synchronization, and API operations.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.exc import IntegrityError
from app import db, session
from models import Item, Customer, Order, SyncLog


class QuickBooksService:
    """Service class for QuickBooks integration operations"""
    
    # QuickBooks API endpoints
    QB_BASE_URL = "https://sandbox-quickbooks.api.intuit.com"  # Change to production URL when ready
    QB_AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
    QB_TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    
    @staticmethod
    def get_connection_status() -> Dict:
        """Get QuickBooks connection status"""
        try:
            # Check if we have valid tokens in session
            access_token = session.get('qb_access_token')
            refresh_token = session.get('qb_refresh_token')
            company_id = session.get('qb_company_id')
            
            if not access_token or not company_id:
                return {
                    'connected': False,
                    'status': 'disconnected',
                    'message': 'Not connected to QuickBooks'
                }
            
            # Check if token is expired
            token_expires = session.get('qb_token_expires')
            if token_expires and datetime.utcnow() > datetime.fromisoformat(token_expires):
                # Try to refresh token
                refresh_result = QuickBooksService._refresh_access_token()
                if not refresh_result['success']:
                    return {
                        'connected': False,
                        'status': 'expired',
                        'message': 'QuickBooks token expired and refresh failed'
                    }
            
            return {
                'connected': True,
                'status': 'connected',
                'company_id': company_id,
                'message': 'Connected to QuickBooks'
            }
            
        except Exception as e:
            return {
                'connected': False,
                'status': 'error',
                'message': f'Error checking connection: {str(e)}'
            }
    
    @staticmethod
    def initiate_oauth_flow() -> Dict:
        """Initiate QuickBooks OAuth flow"""
        try:
            from app import QB_CLIENT_ID, QB_REDIRECT_URI, QB_SCOPE
            
            # Generate state parameter for security
            import secrets
            state = secrets.token_urlsafe(32)
            session['qb_oauth_state'] = state
            
            # Build authorization URL
            auth_url = f"{QuickBooksService.QB_AUTH_URL}?client_id={QB_CLIENT_ID}&scope={QB_SCOPE}&redirect_uri={QB_REDIRECT_URI}&response_type=code&state={state}"
            
            return {
                'success': True,
                'auth_url': auth_url,
                'state': state,
                'message': 'OAuth flow initiated'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to initiate OAuth flow: {str(e)}'
            }
    
    @staticmethod
    def handle_oauth_callback(code: str, state: str) -> Dict:
        """Handle OAuth callback and exchange code for tokens"""
        try:
            from app import QB_CLIENT_ID, QB_CLIENT_SECRET, QB_REDIRECT_URI
            
            # Verify state parameter
            stored_state = session.get('qb_oauth_state')
            if not stored_state or stored_state != state:
                return {
                    'success': False,
                    'error': 'Invalid state parameter'
                }
            
            # Exchange code for tokens
            token_data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': QB_REDIRECT_URI
            }
            
            response = requests.post(
                QuickBooksService.QB_TOKEN_URL,
                data=token_data,
                auth=(QB_CLIENT_ID, QB_CLIENT_SECRET),
                headers={'Accept': 'application/json'}
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Token exchange failed: {response.text}'
                }
            
            token_response = response.json()
            
            # Store tokens in session
            session['qb_access_token'] = token_response['access_token']
            session['qb_refresh_token'] = token_response['refresh_token']
            session['qb_token_expires'] = (datetime.utcnow() + timedelta(seconds=token_response['expires_in'])).isoformat()
            session['qb_company_id'] = token_response.get('realmId')
            
            # Clear OAuth state
            session.pop('qb_oauth_state', None)
            
            return {
                'success': True,
                'company_id': token_response.get('realmId'),
                'message': 'Successfully connected to QuickBooks'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to handle OAuth callback: {str(e)}'
            }
    
    @staticmethod
    def disconnect() -> Dict:
        """Disconnect from QuickBooks"""
        try:
            # Clear all QuickBooks session data
            session.pop('qb_access_token', None)
            session.pop('qb_refresh_token', None)
            session.pop('qb_token_expires', None)
            session.pop('qb_company_id', None)
            session.pop('qb_oauth_state', None)
            
            return {
                'success': True,
                'message': 'Disconnected from QuickBooks'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to disconnect: {str(e)}'
            }
    
    @staticmethod
    def sync_items() -> Dict:
        """Sync items from QuickBooks to local database"""
        try:
            # Check connection status
            connection_status = QuickBooksService.get_connection_status()
            if not connection_status['connected']:
                return {
                    'success': False,
                    'error': 'Not connected to QuickBooks'
                }
            
            # Get items from QuickBooks
            items_response = QuickBooksService._make_qb_api_call('/v3/company/{}/items'.format(session['qb_company_id']))
            
            if not items_response['success']:
                return items_response
            
            items_data = items_response['data']
            synced_count = 0
            error_count = 0
            errors = []
            
            for item_data in items_data.get('QueryResponse', {}).get('Item', []):
                try:
                    # Extract item information
                    qb_id = item_data['Id']
                    name = item_data.get('Name', '')
                    sku = item_data.get('Sku', '')
                    description = item_data.get('Description', '')
                    
                    # Check if item already exists
                    existing_item = Item.query.filter_by(quickbooks_id=qb_id).first()
                    
                    if existing_item:
                        # Update existing item
                        existing_item.name = name
                        existing_item.item_code = sku
                        existing_item.description = description
                        existing_item.updated_at = datetime.utcnow()
                    else:
                        # Create new item
                        new_item = Item(
                            name=name,
                            item_code=sku,
                            description=description,
                            quickbooks_id=qb_id
                        )
                        db.session.add(new_item)
                    
                    synced_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Failed to sync item {qb_id}: {str(e)}")
            
            # Log sync operation
            sync_log = SyncLog(
                sync_type='items',
                status='completed' if error_count == 0 else 'partial',
                message=f'Synced {synced_count} items from QuickBooks',
                records_processed=len(items_data.get('QueryResponse', {}).get('Item', [])),
                records_successful=synced_count,
                records_failed=error_count,
                details=json.dumps(errors) if errors else None
            )
            db.session.add(sync_log)
            db.session.commit()
            
            return {
                'success': True,
                'synced_count': synced_count,
                'error_count': error_count,
                'errors': errors,
                'message': f'Successfully synced {synced_count} items'
            }
            
        except Exception as e:
            # Log error
            sync_log = SyncLog(
                sync_type='items',
                status='error',
                message=f'Failed to sync items: {str(e)}',
                records_processed=0,
                records_successful=0,
                records_failed=0
            )
            db.session.add(sync_log)
            db.session.commit()
            
            return {
                'success': False,
                'error': f'Failed to sync items: {str(e)}'
            }
    
    @staticmethod
    def sync_customers() -> Dict:
        """Sync customers from QuickBooks to local database"""
        try:
            # Check connection status
            connection_status = QuickBooksService.get_connection_status()
            if not connection_status['connected']:
                return {
                    'success': False,
                    'error': 'Not connected to QuickBooks'
                }
            
            # Get customers from QuickBooks
            customers_response = QuickBooksService._make_qb_api_call('/v3/company/{}/customers'.format(session['qb_company_id']))
            
            if not customers_response['success']:
                return customers_response
            
            customers_data = customers_response['data']
            synced_count = 0
            error_count = 0
            errors = []
            
            for customer_data in customers_data.get('QueryResponse', {}).get('Customer', []):
                try:
                    # Extract customer information
                    qb_id = customer_data['Id']
                    name = customer_data.get('Name', '')
                    email = customer_data.get('PrimaryEmailAddr', {}).get('Address', '')
                    phone = customer_data.get('PrimaryPhone', {}).get('FreeFormNumber', '')
                    
                    # Get billing address
                    billing_addr = customer_data.get('BillAddr', {})
                    address = f"{billing_addr.get('Line1', '')} {billing_addr.get('City', '')} {billing_addr.get('CountrySubDivisionCode', '')} {billing_addr.get('PostalCode', '')}".strip()
                    
                    # Check if customer already exists
                    existing_customer = Customer.query.filter_by(quickbooks_id=qb_id).first()
                    
                    if existing_customer:
                        # Update existing customer
                        existing_customer.name = name
                        existing_customer.email = email
                        existing_customer.phone = phone
                        existing_customer.address = address
                    else:
                        # Create new customer
                        new_customer = Customer(
                            name=name,
                            email=email,
                            phone=phone,
                            address=address,
                            quickbooks_id=qb_id
                        )
                        db.session.add(new_customer)
                    
                    synced_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Failed to sync customer {qb_id}: {str(e)}")
            
            # Log sync operation
            sync_log = SyncLog(
                sync_type='customers',
                status='completed' if error_count == 0 else 'partial',
                message=f'Synced {synced_count} customers from QuickBooks',
                records_processed=len(customers_data.get('QueryResponse', {}).get('Customer', [])),
                records_successful=synced_count,
                records_failed=error_count,
                details=json.dumps(errors) if errors else None
            )
            db.session.add(sync_log)
            db.session.commit()
            
            return {
                'success': True,
                'synced_count': synced_count,
                'error_count': error_count,
                'errors': errors,
                'message': f'Successfully synced {synced_count} customers'
            }
            
        except Exception as e:
            # Log error
            sync_log = SyncLog(
                sync_type='customers',
                status='error',
                message=f'Failed to sync customers: {str(e)}',
                records_processed=0,
                records_successful=0,
                records_failed=0
            )
            db.session.add(sync_log)
            db.session.commit()
            
            return {
                'success': False,
                'error': f'Failed to sync customers: {str(e)}'
            }
    
    @staticmethod
    def get_sync_statistics() -> Dict:
        """Get QuickBooks sync statistics"""
        try:
            # Get total counts
            total_items = Item.query.count()
            synced_items = Item.query.filter(Item.quickbooks_id.isnot(None)).count()
            total_customers = Customer.query.count()
            synced_customers = Customer.query.filter(Customer.quickbooks_id.isnot(None)).count()
            
            # Get recent sync activity
            recent_syncs = SyncLog.query.order_by(desc(SyncLog.timestamp)).limit(10).all()
            
            # Get last sync times
            last_item_sync = SyncLog.query.filter_by(sync_type='items').order_by(desc(SyncLog.timestamp)).first()
            last_customer_sync = SyncLog.query.filter_by(sync_type='customers').order_by(desc(SyncLog.timestamp)).first()
            
            return {
                'items': {
                    'total': total_items,
                    'synced': synced_items,
                    'percentage': round((synced_items / total_items * 100) if total_items > 0 else 0, 1),
                    'last_sync': last_item_sync.timestamp.isoformat() if last_item_sync else None
                },
                'customers': {
                    'total': total_customers,
                    'synced': synced_customers,
                    'percentage': round((synced_customers / total_customers * 100) if total_customers > 0 else 0, 1),
                    'last_sync': last_customer_sync.timestamp.isoformat() if last_customer_sync else None
                },
                'recent_activity': [
                    {
                        'id': sync.id,
                        'type': sync.sync_type,
                        'status': sync.status,
                        'message': sync.message,
                        'timestamp': sync.timestamp.isoformat(),
                        'records_processed': sync.records_processed,
                        'records_successful': sync.records_successful,
                        'records_failed': sync.records_failed
                    }
                    for sync in recent_syncs
                ]
            }
            
        except Exception as e:
            raise Exception(f"Failed to retrieve sync statistics: {str(e)}")
    
    @staticmethod
    def get_sync_log() -> List[Dict]:
        """Get QuickBooks sync log"""
        try:
            sync_logs = SyncLog.query.order_by(desc(SyncLog.timestamp)).limit(50).all()
            
            return [
                {
                    'id': log.id,
                    'type': log.sync_type,
                    'status': log.status,
                    'message': log.message,
                    'timestamp': log.timestamp.isoformat(),
                    'records_processed': log.records_processed,
                    'records_successful': log.records_successful,
                    'records_failed': log.records_failed,
                    'details': log.details
                }
                for log in sync_logs
            ]
            
        except Exception as e:
            raise Exception(f"Failed to retrieve sync log: {str(e)}")
    
    @staticmethod
    def get_synced_items() -> List[Dict]:
        """Get items that have been synced with QuickBooks"""
        try:
            items = Item.query.filter(Item.quickbooks_id.isnot(None)).order_by(Item.name.asc()).all()
            
            return [
                {
                    'id': item.id,
                    'name': item.name,
                    'item_code': item.item_code,
                    'quickbooks_id': item.quickbooks_id,
                    'created_at': item.created_at.isoformat() if item.created_at else None,
                    'updated_at': item.updated_at.isoformat() if item.updated_at else None
                }
                for item in items
            ]
            
        except Exception as e:
            raise Exception(f"Failed to retrieve synced items: {str(e)}")
    
    @staticmethod
    def _make_qb_api_call(endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
        """Make API call to QuickBooks"""
        try:
            access_token = session.get('qb_access_token')
            company_id = session.get('qb_company_id')
            
            if not access_token or not company_id:
                return {
                    'success': False,
                    'error': 'Not connected to QuickBooks'
                }
            
            url = f"{QuickBooksService.QB_BASE_URL}{endpoint}"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported HTTP method: {method}'
                }
            
            if response.status_code == 401:
                # Token expired, try to refresh
                refresh_result = QuickBooksService._refresh_access_token()
                if refresh_result['success']:
                    # Retry the request with new token
                    headers['Authorization'] = f'Bearer {session.get("qb_access_token")}'
                    response = requests.get(url, headers=headers)
                else:
                    return {
                        'success': False,
                        'error': 'Token expired and refresh failed'
                    }
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'API call failed: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'API call error: {str(e)}'
            }
    
    @staticmethod
    def _refresh_access_token() -> Dict:
        """Refresh QuickBooks access token"""
        try:
            from app import QB_CLIENT_ID, QB_CLIENT_SECRET
            
            refresh_token = session.get('qb_refresh_token')
            if not refresh_token:
                return {
                    'success': False,
                    'error': 'No refresh token available'
                }
            
            token_data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
            
            response = requests.post(
                QuickBooksService.QB_TOKEN_URL,
                data=token_data,
                auth=(QB_CLIENT_ID, QB_CLIENT_SECRET),
                headers={'Accept': 'application/json'}
            )
            
            if response.status_code == 200:
                token_response = response.json()
                
                # Update session with new tokens
                session['qb_access_token'] = token_response['access_token']
                session['qb_refresh_token'] = token_response['refresh_token']
                session['qb_token_expires'] = (datetime.utcnow() + timedelta(seconds=token_response['expires_in'])).isoformat()
                
                return {
                    'success': True,
                    'message': 'Token refreshed successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f'Token refresh failed: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Token refresh error: {str(e)}'
            }
