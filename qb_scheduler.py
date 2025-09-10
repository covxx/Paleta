#!/usr/bin/env python3
"""
QuickBooks Auto-Sync Scheduler
Handles hourly synchronization of customers, items, orders, and pricing
"""

import schedule
import time
import threading
from datetime import datetime, timezone
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QBScheduler:
    def __init__(self, app):
        self.app = app
        self.running = False
        self.scheduler_thread = None

    def start(self):
        """Start the scheduler in a background thread"""
        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("QuickBooks auto-sync scheduler started")

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("QuickBooks auto-sync scheduler stopped")

    def _run_scheduler(self):
        """Run the scheduler in a background thread"""
        # Schedule hourly sync jobs
        schedule.every().hour.do(self._sync_customers)
        schedule.every().hour.do(self._sync_items)
        schedule.every().hour.do(self._sync_orders)
        schedule.every().hour.do(self._sync_pricing)

        # Run scheduler
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def _sync_customers(self):
        """Sync customers with QuickBooks"""
        with self.app.app_context():
            try:
                from app import import_qb_customers, log_sync_activity

                logger.info("Starting hourly customer sync...")
                result = import_qb_customers()

                if 'error' in result:
                    log_sync_activity('customers', 'error', f'Hourly sync failed: {result["error"]}')
                    logger.error(f"Customer sync failed: {result['error']}")
                else:
                    log_sync_activity('customers', 'success',
                                    f'Hourly sync: {result["customers_imported"]} new, {result["customers_updated"]} updated')
                    logger.info(f"Customer sync completed: {result['customers_imported']} new, {result['customers_updated']} updated")

            except Exception as e:
                logger.error(f"Customer sync error: {str(e)}")
                log_sync_activity('customers', 'error', f'Hourly sync error: {str(e)}')

    def _sync_items(self):
        """Sync items with QuickBooks"""
        with self.app.app_context():
            try:
                from app import import_qb_items, log_sync_activity

                logger.info("Starting hourly item sync...")
                result = import_qb_items()

                if 'error' in result:
                    log_sync_activity('items', 'error', f'Hourly sync failed: {result["error"]}')
                    logger.error(f"Item sync failed: {result['error']}")
                else:
                    log_sync_activity('items', 'success',
                                    f'Hourly sync: {result["items_imported"]} new, {result["items_updated"]} updated')
                    logger.info(f"Item sync completed: {result['items_imported']} new, {result['items_updated']} updated")

            except Exception as e:
                logger.error(f"Item sync error: {str(e)}")
                log_sync_activity('items', 'error', f'Hourly sync error: {str(e)}')

    def _sync_orders(self):
        """Sync pending orders with QuickBooks"""
        with self.app.app_context():
            try:
                from app import Order, create_qb_sales_invoice, log_sync_activity, db

                logger.info("Starting hourly order sync...")

                # Get pending orders
                pending_orders = Order.query.filter_by(quickbooks_synced=False).all()

                synced_count = 0
                errors = []

                for order in pending_orders:
                    try:
                        # Check prerequisites
                        if not order.customer.quickbooks_id:
                            errors.append(f"Order {order.order_number}: Customer not synced")
                            continue

                        unsynced_items = [item for item in order.order_items if not item.item.quickbooks_id]
                        if unsynced_items:
                            item_names = [item.item.name for item in unsynced_items]
                            errors.append(f"Order {order.order_number}: Items not synced: {', '.join(item_names)}")
                            continue

                        # Sync the order
                        result = create_qb_sales_invoice(order)

                        if 'error' in result:
                            errors.append(f"Order {order.order_number}: {result['error']}")
                            continue

                        # Update order
                        order.quickbooks_synced = True
                        order.quickbooks_sync_date = datetime.now(timezone.utc)
                        order.quickbooks_id = result['invoice_id']

                        synced_count += 1

                    except Exception as e:
                        errors.append(f"Order {order.order_number}: {str(e)}")

                db.session.commit()

                if synced_count > 0:
                    log_sync_activity('orders', 'success', f'Hourly sync: {synced_count} orders synced')
                    logger.info(f"Order sync completed: {synced_count} orders synced")

                if errors:
                    logger.warning(f"Order sync had {len(errors)} errors: {errors[:3]}...")

            except Exception as e:
                logger.error(f"Order sync error: {str(e)}")
                log_sync_activity('orders', 'error', f'Hourly sync error: {str(e)}')

    def _sync_pricing(self):
        """Sync customer pricing with QuickBooks"""
        with self.app.app_context():
            try:
                from app import log_sync_activity

                logger.info("Starting hourly pricing sync...")

                # Sync customer pricing from QuickBooks
                try:
                    from app import log_sync_activity
                    log_sync_activity('pricing', 'info', 'Starting customer pricing sync...')

                    # This would implement customer-specific pricing sync
                    # For now, log that it's not implemented yet
                    log_sync_activity('pricing', 'warning', 'Customer pricing sync not yet implemented')

                except Exception as e:
                    logger.error(f"Customer pricing sync failed: {e}")
                    from app import log_sync_activity
                    log_sync_activity('pricing', 'error', f'Customer pricing sync failed: {str(e)}')

                log_sync_activity('pricing', 'success', 'Hourly pricing sync completed')
                logger.info("Pricing sync completed")

            except Exception as e:
                logger.error(f"Pricing sync error: {str(e)}")
                log_sync_activity('pricing', 'error', f'Hourly sync error: {str(e)}')

# Global scheduler instance
qb_scheduler = None

def start_qb_scheduler(app):
    """Start the QuickBooks scheduler"""
    global qb_scheduler
    if qb_scheduler is None:
        qb_scheduler = QBScheduler(app)
        qb_scheduler.start()
    return qb_scheduler

def stop_qb_scheduler():
    """Stop the QuickBooks scheduler"""
    global qb_scheduler
    if qb_scheduler:
        qb_scheduler.stop()
        qb_scheduler = None

if __name__ == "__main__":
    # Test the scheduler
    from app import app

    with app.app_context():
        scheduler = start_qb_scheduler(app)

        try:
            # Run for 5 minutes for testing
            time.sleep(300)
        except KeyboardInterrupt:
            print("Stopping scheduler...")
        finally:
            stop_qb_scheduler()
