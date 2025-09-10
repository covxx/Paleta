"""
Order Service

Handles all business logic related to order management including
order creation, fulfillment, status updates, and customer management.
"""

from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.exc import IntegrityError
from app import db
from app import Order, Customer, Item, Lot

class OrderService:
    """Service class for order management operations"""

    @staticmethod
    def get_all_orders() -> List[Dict]:
        """Get all orders with customer information"""
        try:
            orders = db.session.query(Order, Customer).outerjoin(
                Customer, Order.customer_id == Customer.id
            ).order_by(desc(Order.created_at)).all()

            return [
                {
                    'id': order.id,
                    'order_number': order.order_number,
                    'customer_id': order.customer_id,
                    'customer_name': customer.name if customer else 'Unknown Customer',
                    'status': order.status,
                    'total_amount': float(order.total_amount) if order.total_amount else 0.0,
                    'created_at': order.created_at.isoformat() if order.created_at else None,
                    'quickbooks_synced': order.quickbooks_synced,
                    'items_count': len(order.order_items) if hasattr(order, 'order_items') else 0
                }
                for order, customer in orders
            ]
        except Exception as e:
            raise Exception(f"Failed to retrieve orders: {str(e)}")

    @staticmethod
    def get_order_by_id(order_id: int) -> Optional[Dict]:
        """Get a specific order by ID with full details"""
        try:
            order = Order.query.get(order_id)
            if not order:
                return None

            customer = Customer.query.get(order.customer_id) if order.customer_id else None

            # Get order items (assuming you have an OrderItem model)
            # For now, we'll return basic order info
            return {
                'id': order.id,
                'order_number': order.order_number,
                'customer_id': order.customer_id,
                'customer_name': customer.name if customer else 'Unknown Customer',
                'customer_email': customer.email if customer else None,
                'customer_phone': customer.phone if customer else None,
                'status': order.status,
                'total_amount': float(order.total_amount) if order.total_amount else 0.0,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'quickbooks_synced': order.quickbooks_synced,
                'notes': getattr(order, 'notes', None)
            }
        except Exception as e:
            raise Exception(f"Failed to retrieve order {order_id}: {str(e)}")

    @staticmethod
    def create_order(order_data: Dict) -> Dict:
        """Create a new order"""
        try:
            # Validate required fields
            if not order_data.get('customer_id'):
                raise ValueError("Customer ID is required")

            # Verify customer exists
            customer = Customer.query.get(order_data['customer_id'])
            if not customer:
                raise ValueError(f"Customer with ID {order_data['customer_id']} not found")

            # Generate order number if not provided
            order_number = order_data.get('order_number')
            if not order_number:
                order_number = OrderService._generate_order_number()

            # Check for duplicate order number
            existing_order = Order.query.filter_by(order_number=order_number).first()
            if existing_order:
                raise ValueError(f"Order number '{order_number}' already exists")

            # Create new order
            order = Order(
                order_number=order_number,
                customer_id=order_data['customer_id'],
                status=order_data.get('status', 'pending'),
                total_amount=order_data.get('total_amount', 0.0),
                quickbooks_synced=order_data.get('quickbooks_synced', False)
            )

            db.session.add(order)
            db.session.commit()

            return {
                'id': order.id,
                'order_number': order.order_number,
                'customer_name': customer.name,
                'message': 'Order created successfully'
            }

        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Database integrity error: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create order: {str(e)}")

    @staticmethod
    def update_order(order_id: int, order_data: Dict) -> Dict:
        """Update an existing order"""
        try:
            order = Order.query.get(order_id)
            if not order:
                raise ValueError(f"Order with ID {order_id} not found")

            # Check for duplicate order number (excluding current order)
            if order_data.get('order_number') and order_data['order_number'] != order.order_number:
                existing_order = Order.query.filter(
                    and_(Order.order_number == order_data['order_number'], Order.id != order_id)
                ).first()
                if existing_order:
                    raise ValueError(f"Order number '{order_data['order_number']}' already exists")

            # Update fields
            if 'order_number' in order_data:
                order.order_number = order_data['order_number']
            if 'customer_id' in order_data:
                order.customer_id = order_data['customer_id']
            if 'status' in order_data:
                order.status = order_data['status']
            if 'total_amount' in order_data:
                order.total_amount = order_data['total_amount']
            if 'quickbooks_synced' in order_data:
                order.quickbooks_synced = order_data['quickbooks_synced']

            db.session.commit()

            return {
                'id': order.id,
                'order_number': order.order_number,
                'message': 'Order updated successfully'
            }

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update order: {str(e)}")

    @staticmethod
    def delete_order(order_id: int) -> Dict:
        """Delete an order"""
        try:
            order = Order.query.get(order_id)
            if not order:
                raise ValueError(f"Order with ID {order_id} not found")

            # Check if order can be deleted (e.g., not shipped)
            if order.status in ['shipped', 'delivered']:
                raise ValueError(f"Cannot delete order with status '{order.status}'")

            db.session.delete(order)
            db.session.commit()

            return {
                'id': order_id,
                'message': 'Order deleted successfully'
            }

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete order: {str(e)}")

    @staticmethod
    def update_order_status(order_id: int, new_status: str) -> Dict:
        """Update order status with validation"""
        try:
            valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
            if new_status not in valid_statuses:
                raise ValueError(f"Invalid status '{new_status}'. Valid statuses: {valid_statuses}")

            order = Order.query.get(order_id)
            if not order:
                raise ValueError(f"Order with ID {order_id} not found")

            old_status = order.status
            order.status = new_status
            db.session.commit()

            return {
                'id': order.id,
                'order_number': order.order_number,
                'old_status': old_status,
                'new_status': new_status,
                'message': f'Order status updated from {old_status} to {new_status}'
            }

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update order status: {str(e)}")

    @staticmethod
    def get_orders_by_status(status: str) -> List[Dict]:
        """Get orders filtered by status"""
        try:
            orders = db.session.query(Order, Customer).outerjoin(
                Customer, Order.customer_id == Customer.id
            ).filter(Order.status == status).order_by(desc(Order.created_at)).all()

            return [
                {
                    'id': order.id,
                    'order_number': order.order_number,
                    'customer_name': customer.name if customer else 'Unknown Customer',
                    'total_amount': float(order.total_amount) if order.total_amount else 0.0,
                    'created_at': order.created_at.isoformat() if order.created_at else None,
                    'quickbooks_synced': order.quickbooks_synced
                }
                for order, customer in orders
            ]
        except Exception as e:
            raise Exception(f"Failed to retrieve orders by status: {str(e)}")

    @staticmethod
    def get_orders_by_customer(customer_id: int) -> List[Dict]:
        """Get all orders for a specific customer"""
        try:
            orders = Order.query.filter_by(customer_id=customer_id).order_by(
                desc(Order.created_at)
            ).all()

            return [
                {
                    'id': order.id,
                    'order_number': order.order_number,
                    'status': order.status,
                    'total_amount': float(order.total_amount) if order.total_amount else 0.0,
                    'created_at': order.created_at.isoformat() if order.created_at else None,
                    'quickbooks_synced': order.quickbooks_synced
                }
                for order in orders
            ]
        except Exception as e:
            raise Exception(f"Failed to retrieve orders for customer: {str(e)}")

    @staticmethod
    def get_order_statistics() -> Dict:
        """Get order statistics"""
        try:
            total_orders = Order.query.count()
            pending_orders = Order.query.filter_by(status='pending').count()
            processing_orders = Order.query.filter_by(status='processing').count()
            shipped_orders = Order.query.filter_by(status='shipped').count()
            delivered_orders = Order.query.filter_by(status='delivered').count()
            cancelled_orders = Order.query.filter_by(status='cancelled').count()

            # Calculate total revenue
            total_revenue = db.session.query(
                func.sum(Order.total_amount)
            ).filter(Order.status.in_(['shipped', 'delivered'])).scalar() or 0.0

            # Calculate average order value
            avg_order_value = db.session.query(
                func.avg(Order.total_amount)
            ).filter(Order.status.in_(['shipped', 'delivered'])).scalar() or 0.0

            # Get orders created today
            today = date.today()
            orders_today = Order.query.filter(
                func.date(Order.created_at) == today
            ).count()

            return {
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'processing_orders': processing_orders,
                'shipped_orders': shipped_orders,
                'delivered_orders': delivered_orders,
                'cancelled_orders': cancelled_orders,
                'total_revenue': float(total_revenue),
                'average_order_value': float(avg_order_value),
                'orders_today': orders_today
            }
        except Exception as e:
            raise Exception(f"Failed to retrieve order statistics: {str(e)}")

    @staticmethod
    def _generate_order_number() -> str:
        """Generate a unique order number"""
        try:
            # Get the count of orders created today
            today = date.today()
            today_orders = Order.query.filter(
                func.date(Order.created_at) == today
            ).count()

            # Generate order number: ORD-YYYYMMDD-XXX
            order_number = f"ORD-{today.strftime('%Y%m%d')}-{today_orders + 1:03d}"

            # Ensure uniqueness
            counter = 1
            while Order.query.filter_by(order_number=order_number).first():
                order_number = f"ORD-{today.strftime('%Y%m%d')}-{today_orders + counter:03d}"
                counter += 1

            return order_number

        except Exception as e:
            raise Exception(f"Failed to generate order number: {str(e)}")

    @staticmethod
    def search_orders(search_term: str) -> List[Dict]:
        """Search orders by order number or customer name"""
        try:
            orders = db.session.query(Order, Customer).outerjoin(
                Customer, Order.customer_id == Customer.id
            ).filter(
                or_(
                    Order.order_number.ilike(f'%{search_term}%'),
                    Customer.name.ilike(f'%{search_term}%') if Customer.name else False
                )
            ).order_by(desc(Order.created_at)).all()

            return [
                {
                    'id': order.id,
                    'order_number': order.order_number,
                    'customer_name': customer.name if customer else 'Unknown Customer',
                    'status': order.status,
                    'total_amount': float(order.total_amount) if order.total_amount else 0.0,
                    'created_at': order.created_at.isoformat() if order.created_at else None
                }
                for order, customer in orders
            ]
        except Exception as e:
            raise Exception(f"Failed to search orders: {str(e)}")
