# ProduceFlow Label Printer - Quick Reference Guide

## 🚀 Quick Start

### Access the System
- **URL**: `https://app.srjlabs.dev`
- **Admin Panel**: `https://app.srjlabs.dev/admin`
- **QuickBooks Admin**: `https://app.srjlabs.dev/quickbooks-admin`

### First Time Setup
1. **Add Items**: Receiving → Add Item
2. **Add LOTs**: Receiving → Add LOT
3. **Configure Printers**: Admin Panel → Printer Management
4. **Connect QuickBooks**: Admin Panel → QuickBooks Admin

---

## 📦 Inventory Management

### Adding Items
```
Receiving → Add Item → Fill Details → Save
```

### Adding LOTs
```
Receiving → Add LOT → Select Item → Fill Details → Save
```

### Editing Items
```
Admin Panel → Items Management → Find Item → Edit → Save
```

### Printing Labels
```
Admin Panel → LOT Management → Find LOT → Print
```

---

## 🛒 Order Management

### Creating Orders
```
Orders → New Order → Select Customer → Add Items → Review → Create
```

### Order Statuses
- **Pending**: Order created, awaiting processing
- **Processing**: Order being prepared
- **Shipped**: Order shipped to customer
- **Delivered**: Order delivered to customer
- **Cancelled**: Order cancelled

### Order Fulfillment
```
Orders → Select Order → Check Inventory → Print Labels → Update Status
```

---

## 👥 Customer Management

### Adding Customers
```
Customers → Add Customer → Fill Details → Save
```

### Customer Information
- **Name** (required)
- **Email**
- **Phone**
- **Address**

---

## 🖨️ Label Printing

### Printer Setup
```
Admin Panel → Printer Management → Add Printer → Configure → Test
```

### Printer Configuration
- **Name**: Printer identifier
- **IP Address**: Network IP (e.g., 192.168.1.100)
- **Port**: Usually 9100
- **Type**: Zebra, Datamax, Intermec, Other
- **Label Size**: Width × Height (inches)
- **DPI**: 203, 300, or 600

### Printing Labels
```
LOT Management → Find LOT → Print → Select Printer → Print
```

---

## 🔗 QuickBooks Integration

### Connecting to QuickBooks
```
Admin Panel → QuickBooks Admin → Connect to QB → Login → Authorize
```

### Syncing Data
```
QuickBooks Admin → Manual Sync → Select Type → Sync
```

### Sync Types
- **Items**: Product catalog
- **Customers**: Customer database
- **Orders**: Order data

### Sync Status
- **Connected**: Successfully connected
- **Disconnected**: Not connected
- **Syncing**: Currently syncing
- **Error**: Sync error occurred

---

## 👨‍💼 Admin Panel

### Accessing Admin Panel
```
Main App → Admin Panel → Login → Dashboard
```

### Admin Functions
- **Items Management**: Manage product catalog
- **LOT Management**: Track inventory batches
- **Vendor Management**: Manage suppliers
- **Printer Management**: Configure printers
- **User Management**: Monitor active users
- **QuickBooks Admin**: Manage QB integration

### Admin Dashboard
- **System Overview**: Key metrics
- **Quick Actions**: Direct access to functions
- **Health Status**: System health indicators
- **Recent Activity**: Admin activity log

---

## 🔧 Common Operations

### Adding New Inventory
1. **Add Item** (if not exists)
2. **Add LOT** for the item
3. **Print Label** for the LOT
4. **Update Quantities** as needed

### Processing Orders
1. **Create Order** with customer
2. **Add Items** to order
3. **Check Inventory** availability
4. **Print Labels** for items
5. **Update Order Status**

### Managing Expiry Dates
1. **Go to LOT Management**
2. **Sort by Expiry Date**
3. **Check Expiring Items**
4. **Update Status** if needed
5. **Print New Labels** if required

### QuickBooks Sync
1. **Check Connection Status**
2. **Run Manual Sync** if needed
3. **Check Sync Logs** for errors
4. **Verify Data** in QuickBooks

---

## ⌨️ Keyboard Shortcuts

### Navigation
- **Ctrl + H**: Dashboard
- **Ctrl + R**: Receiving
- **Ctrl + O**: Orders
- **Ctrl + C**: Customers
- **Ctrl + A**: Admin Panel

### Actions
- **Ctrl + N**: New Order
- **Ctrl + S**: Save
- **Ctrl + P**: Print
- **Ctrl + F**: Search
- **Esc**: Cancel/Close

### Quick Access
- **F1**: Help
- **F5**: Refresh
- **Ctrl + +**: Zoom In
- **Ctrl + -**: Zoom Out

---

## 🚨 Troubleshooting

### Can't Print Labels
1. **Check Printer Connection**
   - Verify IP address
   - Test network connectivity
   - Check printer status
2. **Check Printer Configuration**
   - Verify port settings
   - Check label dimensions
   - Test printer connection

### QuickBooks Sync Issues
1. **Check Connection Status**
2. **Verify QuickBooks Credentials**
3. **Check Sync Logs** for errors
4. **Reconnect to QuickBooks** if needed

### Slow Performance
1. **Check System Resources**
2. **Clear Browser Cache**
3. **Restart Application** if needed
4. **Contact Administrator**

### Data Not Saving
1. **Check Internet Connection**
2. **Verify Required Fields** are filled
3. **Try Refreshing** the page
4. **Contact Administrator** if issue persists

---

## 📊 System Status

### Health Checks
- **Database**: Connection status
- **Printers**: Online/offline status
- **QuickBooks**: Sync status
- **Auto-Sync**: Background sync status

### Performance Metrics
- **Page Load Time**: < 2 seconds
- **API Response Time**: < 500ms
- **Database Queries**: < 100ms
- **Label Generation**: < 1 second

---

## 🔒 Security

### Best Practices
- **Use Strong Passwords**
- **Don't Share Passwords**
- **Logout When Finished**
- **Don't Leave System Unattended**
- **Report Suspicious Activity**

### Data Protection
- **Use Secure Connections** (HTTPS)
- **Don't Use Public Wi-Fi** for sensitive operations
- **Keep System Updated**
- **Report Security Issues**

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

## 🆘 Emergency Procedures

### System Down
1. **Check Internet Connection**
2. **Try Refreshing** the page
3. **Contact Administrator**
4. **Use Backup Procedures** if available

### Data Loss
1. **Don't Panic**
2. **Contact Administrator** immediately
3. **Provide Details** of what was lost
4. **Wait for Recovery** instructions

### Printer Issues
1. **Check Printer Power**
2. **Verify Network Connection**
3. **Test with Other Applications**
4. **Contact IT Support**

---

## 📞 Support Contacts

### System Administrator
- **Email**: admin@srjlabs.dev
- **Phone**: (555) 123-4567
- **Hours**: Monday-Friday, 9AM-5PM EST

### Technical Support
- **Email**: support@srjlabs.dev
- **Phone**: (555) 123-4568
- **Hours**: 24/7 Emergency Support

### QuickBooks Support
- **Email**: qb-support@srjlabs.dev
- **Phone**: (555) 123-4569
- **Hours**: Monday-Friday, 8AM-6PM EST

---

## 📋 Checklist

### Daily Tasks
- [ ] Check system health
- [ ] Review recent orders
- [ ] Check printer status
- [ ] Verify QuickBooks sync

### Weekly Tasks
- [ ] Review inventory levels
- [ ] Check expiry dates
- [ ] Update customer information
- [ ] Backup system data

### Monthly Tasks
- [ ] Review system performance
- [ ] Update passwords
- [ ] Check security settings
- [ ] Plan system updates

---

*This quick reference guide provides essential information for daily operations with the ProduceFlow Label Printer system. For detailed information, refer to the complete User Manual and Technical Documentation.*
