"""
Customer Service

Handles all business logic related to customer management including
customer creation, updates, and order history.
"""

from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.exc import IntegrityError
from app import db
from app import Customer, Order

class CustomerService:
    """Service class for customer management operations"""

    @staticmethod
    def get_all_customers() -> List[Dict]:
        """Get all customers with order statistics"""
        try:
            customers = Customer.query.order_by(Customer.name.asc()).all()

            result = []
            for customer in customers:
                # Get order statistics for this customer
                total_orders = Order.query.filter_by(customer_id=customer.id).count()
                total_spent = db.session.query(
                    func.sum(Order.total_amount)
                ).filter(
                    and_(
                        Order.customer_id == customer.id,
                        Order.status.in_(['shipped', 'delivered'])
                    )
                ).scalar() or 0.0

                # Get last order date
                last_order = Order.query.filter_by(customer_id=customer.id).order_by(
                    desc(Order.created_at)
                ).first()

                result.append({
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email,
                    'phone': customer.phone,
                    'address': customer.address,
                    'quickbooks_id': customer.quickbooks_id,
                    'created_at': customer.created_at.isoformat() if customer.created_at else None,
                    'total_orders': total_orders,
                    'total_spent': float(total_spent),
                    'last_order_date': last_order.created_at.isoformat() if last_order else None,
                    'average_order_value': float(total_spent / total_orders) if total_orders > 0 else 0.0
                })

            return result
        except Exception as e:
            raise Exception(f"Failed to retrieve customers: {str(e)}")

    @staticmethod
    def get_customer_by_id(customer_id: int) -> Optional[Dict]:
        """Get a specific customer by ID with order history"""
        try:
            customer = Customer.query.get(customer_id)
            if not customer:
                return None

            # Get order history
            orders = Order.query.filter_by(customer_id=customer_id).order_by(
                desc(Order.created_at)
            ).all()

            # Calculate statistics
            total_orders = len(orders)
            total_spent = sum(
                float(order.total_amount) for order in orders
                if order.status in ['shipped', 'delivered'] and order.total_amount
            )

            return {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
                'address': customer.address,
                'quickbooks_id': customer.quickbooks_id,
                'created_at': customer.created_at.isoformat() if customer.created_at else None,
                'total_orders': total_orders,
                'total_spent': total_spent,
                'average_order_value': total_spent / total_orders if total_orders > 0 else 0.0,
                'orders': [
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
            }
        except Exception as e:
            raise Exception(f"Failed to retrieve customer {customer_id}: {str(e)}")

    @staticmethod
    def create_customer(customer_data: Dict) -> Dict:
        """Create a new customer"""
        try:
            # Validate required fields
            if not customer_data.get('name'):
                raise ValueError("Customer name is required")

            # Check for duplicate email if provided
            if customer_data.get('email'):
                existing_customer = Customer.query.filter_by(email=customer_data['email']).first()
                if existing_customer:
                    raise ValueError(f"Customer with email '{customer_data['email']}' already exists")

            # Create new customer
            customer = Customer(
                name=customer_data['name'],
                email=customer_data.get('email'),
                phone=customer_data.get('phone'),
                address=customer_data.get('address'),
                quickbooks_id=customer_data.get('quickbooks_id')
            )

            db.session.add(customer)
            db.session.commit()

            return {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'message': 'Customer created successfully'
            }

        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Database integrity error: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create customer: {str(e)}")

    @staticmethod
    def update_customer(customer_id: int, customer_data: Dict) -> Dict:
        """Update an existing customer"""
        try:
            customer = Customer.query.get(customer_id)
            if not customer:
                raise ValueError(f"Customer with ID {customer_id} not found")

            # Check for duplicate email (excluding current customer)
            if customer_data.get('email') and customer_data['email'] != customer.email:
                existing_customer = Customer.query.filter(
                    and_(Customer.email == customer_data['email'], Customer.id != customer_id)
                ).first()
                if existing_customer:
                    raise ValueError(f"Customer with email '{customer_data['email']}' already exists")

            # Update fields
            if 'name' in customer_data:
                customer.name = customer_data['name']
            if 'email' in customer_data:
                customer.email = customer_data['email']
            if 'phone' in customer_data:
                customer.phone = customer_data['phone']
            if 'address' in customer_data:
                customer.address = customer_data['address']
            if 'quickbooks_id' in customer_data:
                customer.quickbooks_id = customer_data['quickbooks_id']

            db.session.commit()

            return {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'message': 'Customer updated successfully'
            }

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update customer: {str(e)}")

    @staticmethod
    def delete_customer(customer_id: int) -> Dict:
        """Delete a customer (soft delete by checking for orders)"""
        try:
            customer = Customer.query.get(customer_id)
            if not customer:
                raise ValueError(f"Customer with ID {customer_id} not found")

            # Check if customer has orders
            order_count = Order.query.filter_by(customer_id=customer_id).count()
            if order_count > 0:
                raise ValueError(f"Cannot delete customer with {order_count} orders")

            db.session.delete(customer)
            db.session.commit()

            return {
                'id': customer_id,
                'message': 'Customer deleted successfully'
            }

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete customer: {str(e)}")

    @staticmethod
    def search_customers(search_term: str) -> List[Dict]:
        """Search customers by name, email, or phone"""
        try:
            customers = Customer.query.filter(
                or_(
                    Customer.name.ilike(f'%{search_term}%'),
                    Customer.email.ilike(f'%{search_term}%'),
                    Customer.phone.ilike(f'%{search_term}%')
                )
            ).order_by(Customer.name.asc()).all()

            result = []
            for customer in customers:
                # Get basic order statistics
                total_orders = Order.query.filter_by(customer_id=customer.id).count()
                total_spent = db.session.query(
                    func.sum(Order.total_amount)
                ).filter(
                    and_(
                        Order.customer_id == customer.id,
                        Order.status.in_(['shipped', 'delivered'])
                    )
                ).scalar() or 0.0

                result.append({
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email,
                    'phone': customer.phone,
                    'address': customer.address,
                    'quickbooks_id': customer.quickbooks_id,
                    'created_at': customer.created_at.isoformat() if customer.created_at else None,
                    'total_orders': total_orders,
                    'total_spent': float(total_spent)
                })

            return result
        except Exception as e:
            raise Exception(f"Failed to search customers: {str(e)}")

    @staticmethod
    def get_customer_statistics() -> Dict:
        """Get customer statistics"""
        try:
            total_customers = Customer.query.count()

            # Customers with orders
            customers_with_orders = db.session.query(
                func.count(func.distinct(Order.customer_id))
            ).scalar() or 0

            # Top customers by total spent
            top_customers = db.session.query(
                Customer.name,
                func.sum(Order.total_amount).label('total_spent')
            ).join(Order, Customer.id == Order.customer_id).filter(
                Order.status.in_(['shipped', 'delivered'])
            ).group_by(Customer.id, Customer.name).order_by(
                desc('total_spent')
            ).limit(5).all()

            # New customers this month
            from datetime import datetime, date
            current_month = date.today().replace(day=1)
            new_customers_this_month = Customer.query.filter(
                func.date(Customer.created_at) >= current_month
            ).count()

            return {
                'total_customers': total_customers,
                'customers_with_orders': customers_with_orders,
                'new_customers_this_month': new_customers_this_month,
                'top_customers': [
                    {
                        'name': customer.name,
                        'total_spent': float(total_spent)
                    }
                    for customer, total_spent in top_customers
                ]
            }
        except Exception as e:
            raise Exception(f"Failed to retrieve customer statistics: {str(e)}")

    @staticmethod
    def get_customers_by_quickbooks_sync_status(synced: bool = True) -> List[Dict]:
        """Get customers filtered by QuickBooks sync status"""
        try:
            if synced:
                customers = Customer.query.filter(
                    Customer.quickbooks_id.isnot(None)
                ).order_by(Customer.name.asc()).all()
            else:
                customers = Customer.query.filter(
                    Customer.quickbooks_id.is_(None)
                ).order_by(Customer.name.asc()).all()

            return [
                {
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email,
                    'phone': customer.phone,
                    'quickbooks_id': customer.quickbooks_id,
                    'created_at': customer.created_at.isoformat() if customer.created_at else None
                }
                for customer in customers
            ]
        except Exception as e:
            raise Exception(f"Failed to retrieve customers by sync status: {str(e)}")

    @staticmethod
    def bulk_update_quickbooks_ids(updates: List[Dict]) -> Dict:
        """Bulk update QuickBooks IDs for customers"""
        try:
            updated_count = 0
            errors = []

            for update in updates:
                try:
                    customer_id = update.get('customer_id')
                    quickbooks_id = update.get('quickbooks_id')

                    if not customer_id or not quickbooks_id:
                        errors.append(f"Invalid update data: {update}")
                        continue

                    customer = Customer.query.get(customer_id)
                    if not customer:
                        errors.append(f"Customer {customer_id} not found")
                        continue

                    customer.quickbooks_id = quickbooks_id
                    updated_count += 1

                except Exception as e:
                    errors.append(f"Failed to update customer {customer_id}: {str(e)}")

            db.session.commit()

            return {
                'updated_count': updated_count,
                'error_count': len(errors),
                'errors': errors,
                'message': f'Updated {updated_count} customers successfully'
            }

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to bulk update QuickBooks IDs: {str(e)}")
