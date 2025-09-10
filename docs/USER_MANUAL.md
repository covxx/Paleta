# ProduceFlow Label Printer - User Manual

## 📋 Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Inventory Management](#inventory-management)
4. [Order Management](#order-management)
5. [Customer Management](#customer-management)
6. [Label Printing](#label-printing)
7. [QuickBooks Integration](#quickbooks-integration)
8. [Admin Panel](#admin-panel)
9. [Troubleshooting](#troubleshooting)
10. [Keyboard Shortcuts](#keyboard-shortcuts)

---

## 🚀 Getting Started

### Accessing the System
1. **Open your web browser**
2. **Navigate to**: `https://app.srjlabs.dev`
3. **Login** (if required) or start using the system

### First Time Setup
1. **Configure Printers**: Go to Admin Panel → Printer Management
2. **Add Items**: Go to Receiving → Add Items
3. **Setup Vendors**: Go to Receiving → Manage Vendors
4. **Connect QuickBooks**: Go to Admin Panel → QuickBooks Admin

---

## 📊 Dashboard Overview

The dashboard provides a quick overview of your system status and key metrics.

### Key Statistics
- **Total Items**: Number of products in your catalog
- **Total LOTs**: Number of inventory batches
- **Vendors**: Number of suppliers
- **Printers**: Number of configured printers

### Quick Actions
- **Receiving**: Add new inventory
- **New Order**: Create customer orders
- **Label Designer**: Design custom labels
- **Admin Panel**: System management

### Recent Activity
- **Latest Actions**: Recent system activities
- **Order Status**: Current order statuses
- **System Events**: Important system notifications

### System Status
- **Database**: Connection status
- **Printers**: Online/offline status
- **QuickBooks**: Sync status
- **Auto-Sync**: Background sync status

---

## 📦 Inventory Management

### Adding Items
1. **Go to Receiving** page
2. **Click "Add Item"** button
3. **Fill in item details**:
   - Item Name (required)
   - Item Code (unique identifier)
   - GTIN (barcode)
   - Category
   - Description
   - Unit Price
4. **Click "Save Item"**

### Managing LOTs
1. **Go to Receiving** page
2. **Click "Add LOT"** button
3. **Select Item** from dropdown
4. **Enter LOT details**:
   - LOT Code (unique identifier)
   - Quantity
   - Unit (pcs, lbs, kg, etc.)
   - Expiry Date
   - Vendor
5. **Click "Save LOT"**

### Editing Items
1. **Go to Admin Panel** → Items Management
2. **Find the item** you want to edit
3. **Click the Edit button** (pencil icon)
4. **Make your changes**
5. **Click "Save"**

### Deleting Items
1. **Go to Admin Panel** → Items Management
2. **Find the item** you want to delete
3. **Click the Delete button** (trash icon)
4. **Confirm deletion**

---

## 🛒 Order Management

### Creating New Orders
1. **Go to Orders** page
2. **Click "New Order"** button
3. **Select Customer**:
   - Choose existing customer, or
   - Create new customer
4. **Add Items**:
   - Search for items
   - Select items and quantities
   - Review pricing
5. **Review Order**:
   - Check items and quantities
   - Verify pricing
   - Add notes if needed
6. **Click "Create Order"**

### Managing Orders
1. **Go to Orders** page
2. **View order list** with status filters
3. **Click on order** to view details
4. **Update status**:
   - Pending → Processing
   - Processing → Shipped
   - Shipped → Delivered
5. **Print labels** for order items

### Order Statuses
- **Pending**: Order created, awaiting processing
- **Processing**: Order being prepared
- **Shipped**: Order shipped to customer
- **Delivered**: Order delivered to customer
- **Cancelled**: Order cancelled

### Order Fulfillment
1. **Select order** to fulfill
2. **Check inventory** availability
3. **Print labels** for items
4. **Update quantities** if needed
5. **Change status** to "Shipped"

---

## 👥 Customer Management

### Adding Customers
1. **Go to Customers** page
2. **Click "Add Customer"** button
3. **Enter customer details**:
   - Name (required)
   - Email address
   - Phone number
   - Address
4. **Click "Save Customer"**

### Managing Customers
1. **Go to Customers** page
2. **Search for customer** using search bar
3. **Click on customer** to view details
4. **View order history**
5. **Edit customer information**

### Customer Information
- **Contact Details**: Name, email, phone, address
- **Order History**: All past orders
- **QuickBooks Sync**: Sync status with QuickBooks
- **Notes**: Additional customer information

---

## 🖨️ Label Printing

### Printing Individual Labels
1. **Go to LOT Management** (Admin Panel)
2. **Find the LOT** you want to print
3. **Click "Print"** button
4. **Select printer** (if multiple printers)
5. **Click "Print Label"**

### Batch Label Printing
1. **Go to Orders** page
2. **Select order** to print labels for
3. **Click "Print All Labels"**
4. **Select printer**
5. **Click "Print"**

### Label Information
- **Item Name**: Product name
- **LOT Code**: Batch identifier
- **Expiry Date**: Expiration date
- **Barcode**: Scannable barcode
- **Company Info**: Your business information

### Printer Management
1. **Go to Admin Panel** → Printer Management
2. **Add Printer**:
   - Name
   - IP Address
   - Port (usually 9100)
   - Printer Type (Zebra, Datamax, etc.)
   - Label dimensions
3. **Test Connection** to verify setup
4. **Configure label settings**

---

## 🔗 QuickBooks Integration

### Connecting to QuickBooks
1. **Go to Admin Panel** → QuickBooks Admin
2. **Click "Connect to QB"**
3. **Login to QuickBooks** Online
4. **Authorize the connection**
5. **Select company** to connect

### Syncing Data
1. **Go to QuickBooks Admin** page
2. **View sync status** and statistics
3. **Manual Sync**:
   - Click "Sync Items" to sync products
   - Click "Sync Customers" to sync customers
   - Click "Sync Orders" to sync orders
4. **View sync logs** for detailed information

### Sync Status
- **Connected**: Successfully connected to QuickBooks
- **Disconnected**: Not connected to QuickBooks
- **Syncing**: Currently syncing data
- **Error**: Sync error occurred

### Data Synchronization
- **Items**: Product catalog sync
- **Customers**: Customer database sync
- **Orders**: Order data sync
- **Pricing**: Price updates sync

---

## 👨‍💼 Admin Panel

### Accessing Admin Panel
1. **Click "Admin Panel"** from main navigation
2. **Login** with admin credentials
3. **Access management functions**

### Admin Dashboard
- **System Overview**: Key metrics and statistics
- **Quick Actions**: Direct access to management functions
- **Health Status**: System health indicators
- **Recent Activity**: Admin activity log

### Items Management
- **View all items** in catalog
- **Add new items**
- **Edit existing items**
- **Delete items**
- **Bulk operations**

### LOT Management
- **View all LOTs**
- **Track expiry dates**
- **Monitor quantities**
- **Update LOT status**
- **Print labels**

### Vendor Management
- **Manage suppliers**
- **Contact information**
- **Performance tracking**
- **Order history**

### Printer Management
- **Configure printers**
- **Test connections**
- **Manage label templates**
- **Monitor print queue**

### User Management
- **View active users**
- **Monitor user activity**
- **Session management**
- **Access control**

### QuickBooks Admin
- **Connection management**
- **Sync operations**
- **Data mapping**
- **Error handling**

---

## 🔧 Troubleshooting

### Common Issues

#### Can't Print Labels
1. **Check printer connection**:
   - Verify IP address
   - Test network connectivity
   - Check printer status
2. **Check printer configuration**:
   - Verify port settings
   - Check label dimensions
   - Test printer connection

#### QuickBooks Sync Issues
1. **Check connection status**
2. **Verify QuickBooks credentials**
3. **Check sync logs** for errors
4. **Reconnect to QuickBooks** if needed

#### Slow Performance
1. **Check system resources**
2. **Clear browser cache**
3. **Restart application** if needed
4. **Contact administrator**

#### Data Not Saving
1. **Check internet connection**
2. **Verify required fields** are filled
3. **Try refreshing the page**
4. **Contact administrator** if issue persists

### Getting Help
1. **Check this manual** for common solutions
2. **Contact your system administrator**
3. **Check system logs** for error details
4. **Report issues** with detailed descriptions

---

## ⌨️ Keyboard Shortcuts

### Navigation
- **Ctrl + H**: Go to Dashboard
- **Ctrl + R**: Go to Receiving
- **Ctrl + O**: Go to Orders
- **Ctrl + C**: Go to Customers
- **Ctrl + A**: Go to Admin Panel

### Actions
- **Ctrl + N**: New Order
- **Ctrl + S**: Save
- **Ctrl + P**: Print
- **Ctrl + F**: Search/Find
- **Esc**: Cancel/Close

### Quick Access
- **F1**: Help
- **F5**: Refresh
- **Ctrl + R**: Refresh
- **Ctrl + +**: Zoom In
- **Ctrl + -**: Zoom Out

---

## 📱 Mobile Usage

### Mobile Browser Support
- **Chrome Mobile**: Full support
- **Safari Mobile**: Full support
- **Firefox Mobile**: Full support
- **Edge Mobile**: Full support

### Mobile Features
- **Responsive Design**: Works on all screen sizes
- **Touch-Friendly**: Optimized for touch interfaces
- **Mobile Navigation**: Easy mobile navigation
- **Quick Actions**: Mobile-optimized quick actions

### Mobile Limitations
- **Label Printing**: Requires network printer
- **Bulk Operations**: Limited on mobile
- **Admin Functions**: Some functions desktop-only

---

## 🔒 Security Best Practices

### Password Security
- **Use strong passwords**
- **Don't share passwords**
- **Change passwords regularly**
- **Use unique passwords**

### Data Protection
- **Logout when finished**
- **Don't leave system unattended**
- **Report suspicious activity**
- **Keep system updated**

### Network Security
- **Use secure connections** (HTTPS)
- **Don't use public Wi-Fi** for sensitive operations
- **Keep network secure**
- **Report security issues**

---

## 📊 Reports and Analytics

### Available Reports
- **Inventory Reports**: Stock levels, expiry dates
- **Order Reports**: Order history, customer orders
- **Sales Reports**: Revenue, top items
- **Vendor Reports**: Supplier performance

### Generating Reports
1. **Go to Admin Panel** → Analytics
2. **Select report type**
3. **Choose date range**
4. **Click "Generate Report"**
5. **Export or print** report

### Data Export
- **CSV Export**: Export data to Excel
- **PDF Reports**: Generate PDF reports
- **Print Reports**: Print directly
- **Email Reports**: Send via email

---

## 🆘 Emergency Procedures

### System Down
1. **Check internet connection**
2. **Try refreshing the page**
3. **Contact administrator**
4. **Use backup procedures** if available

### Data Loss
1. **Don't panic**
2. **Contact administrator immediately**
3. **Provide details** of what was lost
4. **Wait for recovery** instructions

### Printer Issues
1. **Check printer power**
2. **Verify network connection**
3. **Test with other applications**
4. **Contact IT support**

---

*This user manual provides comprehensive guidance for using the ProduceFlow Label Printer system. For additional support, contact your system administrator.*
