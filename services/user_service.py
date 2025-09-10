"""
User Service

Handles all business logic related to user management including
admin users, active sessions, and user authentication.
"""

import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, session, active_sessions, session_lock, AdminUser

class UserService:
    """Service class for user management operations"""

    @staticmethod
    def get_all_admin_users() -> List[Dict]:
        """Get all admin users"""
        try:
            users = AdminUser.query.order_by(AdminUser.first_name.asc()).all()

            return [
                {
                    'id': user.id,
                    'email': user.email,
                    'name': f"{user.first_name} {user.last_name}".strip(),
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'is_active': user.is_active
                }
                for user in users
            ]
        except Exception as e:
            raise Exception(f"Failed to retrieve admin users: {str(e)}")

    @staticmethod
    def get_admin_user_by_id(user_id: int) -> Optional[Dict]:
        """Get a specific admin user by ID"""
        try:
            user = AdminUser.query.get(user_id)
            if not user:
                return None

            return {
                'id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip(),
                'first_name': user.first_name,
                'last_name': user.last_name,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_active': user.is_active
            }
        except Exception as e:
            raise Exception(f"Failed to retrieve admin user {user_id}: {str(e)}")

    @staticmethod
    def create_admin_user(user_data: Dict) -> Dict:
        """Create a new admin user"""
        try:
            # Validate required fields
            if not user_data.get('email'):
                raise ValueError("Email is required")
            if not user_data.get('password'):
                raise ValueError("Password is required")
            if not user_data.get('first_name'):
                raise ValueError("First name is required")
            if not user_data.get('last_name'):
                raise ValueError("Last name is required")

            # Check for duplicate email
            existing_user = AdminUser.query.filter_by(email=user_data['email']).first()
            if existing_user:
                raise ValueError(f"User with email '{user_data['email']}' already exists")

            # Validate email format
            from utils.validation_utils import validate_email
            if not validate_email(user_data['email']):
                raise ValueError("Invalid email format")

            # Validate password strength
            password = user_data['password']
            if len(password) < 8:
                raise ValueError("Password must be at least 8 characters long")

            # Create new admin user
            user = AdminUser(
                email=user_data['email'],
                password_hash=generate_password_hash(password),
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )

            db.session.add(user)
            db.session.commit()

            return {
                'id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip(),
                'first_name': user.first_name,
                'last_name': user.last_name,
                'message': 'Admin user created successfully'
            }

        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Database integrity error: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create admin user: {str(e)}")

    @staticmethod
    def update_admin_user(user_id: int, user_data: Dict) -> Dict:
        """Update an existing admin user"""
        try:
            user = AdminUser.query.get(user_id)
            if not user:
                raise ValueError(f"Admin user with ID {user_id} not found")

            # Check for duplicate email (excluding current user)
            if user_data.get('email') and user_data['email'] != user.email:
                existing_user = AdminUser.query.filter(
                    and_(AdminUser.email == user_data['email'], AdminUser.id != user_id)
                ).first()
                if existing_user:
                    raise ValueError(f"User with email '{user_data['email']}' already exists")

                # Validate email format
                from utils.validation_utils import validate_email
                if not validate_email(user_data['email']):
                    raise ValueError("Invalid email format")

            # Update fields
            if 'email' in user_data:
                user.email = user_data['email']
            if 'first_name' in user_data:
                user.first_name = user_data['first_name']
            if 'last_name' in user_data:
                user.last_name = user_data['last_name']
            if 'password' in user_data and user_data['password']:
                # Validate password strength
                password = user_data['password']
                if len(password) < 8:
                    raise ValueError("Password must be at least 8 characters long")
                user.password_hash = generate_password_hash(password)

            db.session.commit()

            return {
                'id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip(),
                'first_name': user.first_name,
                'last_name': user.last_name,
                'message': 'Admin user updated successfully'
            }

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update admin user: {str(e)}")

    @staticmethod
    def delete_admin_user(user_id: int) -> Dict:
        """Delete an admin user"""
        try:
            user = AdminUser.query.get(user_id)
            if not user:
                raise ValueError(f"Admin user with ID {user_id} not found")

            # Prevent deleting the last admin user
            total_users = AdminUser.query.count()
            if total_users <= 1:
                raise ValueError("Cannot delete the last admin user")

            # Check if user is currently logged in
            if session.get('admin_email') == user.email:
                raise ValueError("Cannot delete currently logged in user")

            db.session.delete(user)
            db.session.commit()

            return {
                'id': user_id,
                'message': 'Admin user deleted successfully'
            }

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete admin user: {str(e)}")

    @staticmethod
    def get_active_users() -> List[Dict]:
        """Get currently active users from session tracking"""
        try:
            current_time = time.time()
            active_users = []

            with session_lock:
                for user_id, data in active_sessions.items():
                    # Only include sessions active in last 10 minutes
                    if current_time - data['last_activity'] < 600:
                        session_duration = current_time - data.get('session_start', data['last_activity'])
                        active_users.append({
                            'user_id': user_id,
                            'email': data['email'],
                            'ip_address': data['ip_address'],
                            'last_activity': data['last_activity'],
                            'session_duration': session_duration,
                            'minutes_ago': int((current_time - data['last_activity']) / 60)
                        })

            # Sort by last activity (most recent first)
            active_users.sort(key=lambda x: x['last_activity'], reverse=True)

            return active_users

        except Exception as e:
            raise Exception(f"Failed to retrieve active users: {str(e)}")

    @staticmethod
    def kick_user(user_id: str) -> Dict:
        """Kick a user by removing their session"""
        try:
            with session_lock:
                if user_id in active_sessions:
                    user_data = active_sessions[user_id]
                    del active_sessions[user_id]

                    return {
                        'user_id': user_id,
                        'email': user_data.get('email', 'Unknown'),
                        'message': 'User session terminated successfully'
                    }
                else:
                    raise ValueError(f"User {user_id} not found in active sessions")

        except Exception as e:
            raise Exception(f"Failed to kick user: {str(e)}")

    @staticmethod
    def get_user_statistics() -> Dict:
        """Get user statistics"""
        try:
            total_admin_users = AdminUser.query.count()

            # Get active users count
            current_time = time.time()
            active_count = 0

            with session_lock:
                for user_id, data in active_sessions.items():
                    if current_time - data['last_activity'] < 600:  # 10 minutes
                        active_count += 1

            # Get users created this month
            from datetime import date
            current_month = date.today().replace(day=1)
            new_users_this_month = AdminUser.query.filter(
                func.date(AdminUser.created_at) >= current_month
            ).count()

            # Get last login statistics
            recent_logins = AdminUser.query.filter(
                AdminUser.last_login.isnot(None)
            ).order_by(desc(AdminUser.last_login)).limit(5).all()

            return {
                'total_admin_users': total_admin_users,
                'active_users': active_count,
                'new_users_this_month': new_users_this_month,
                'recent_logins': [
                    {
                        'email': user.email,
                        'name': f"{user.first_name} {user.last_name}".strip(),
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'last_login': user.last_login.isoformat() if user.last_login else None
                    }
                    for user in recent_logins
                ]
            }

        except Exception as e:
            raise Exception(f"Failed to retrieve user statistics: {str(e)}")

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict]:
        """Authenticate a user"""
        try:
            user = AdminUser.query.filter_by(email=email).first()
            if not user:
                return None

            if check_password_hash(user.password_hash, password):
                # Update last login
                user.last_login = datetime.utcnow()
                db.session.commit()

                return {
                    'id': user.id,
                    'email': user.email,
                    'name': f"{user.first_name} {user.last_name}".strip(),
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }

            return None

        except Exception as e:
            raise Exception(f"Failed to authenticate user: {str(e)}")

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> Dict:
        """Change user password"""
        try:
            user = AdminUser.query.get(user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} not found")

            # Verify old password
            if not check_password_hash(user.password_hash, old_password):
                raise ValueError("Current password is incorrect")

            # Validate new password
            if len(new_password) < 8:
                raise ValueError("New password must be at least 8 characters long")

            # Update password
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()

            return {
                'id': user_id,
                'message': 'Password changed successfully'
            }

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to change password: {str(e)}")

    @staticmethod
    def search_users(search_term: str) -> List[Dict]:
        """Search users by name or email"""
        try:
            users = AdminUser.query.filter(
                or_(
                    AdminUser.first_name.ilike(f'%{search_term}%'),
                    AdminUser.last_name.ilike(f'%{search_term}%'),
                    AdminUser.email.ilike(f'%{search_term}%')
                )
            ).order_by(AdminUser.first_name.asc()).all()

            return [
                {
                    'id': user.id,
                    'email': user.email,
                    'name': f"{user.first_name} {user.last_name}".strip(),
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
                for user in users
            ]
        except Exception as e:
            raise Exception(f"Failed to search users: {str(e)}")
