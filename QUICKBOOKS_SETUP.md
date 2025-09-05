# QuickBooks Online Integration Setup Guide

This guide will help you set up QuickBooks Online integration for importing customers and items into your inventory system.

## Prerequisites

1. **QuickBooks Online Account**: You need an active QuickBooks Online subscription
2. **Intuit Developer Account**: Create an account at [developer.intuit.com](https://developer.intuit.com)
3. **QuickBooks App**: Create a new app in the Intuit Developer Dashboard

## Step 1: Create QuickBooks App

1. Go to [developer.intuit.com](https://developer.intuit.com)
2. Sign in with your Intuit account
3. Click "Create an app"
4. Choose "QuickBooks Online API"
5. Fill in the app details:
   - **App Name**: Your inventory system name
   - **App Description**: Brief description of your app
   - **Redirect URI**: `http://localhost:5001/qb/callback` (for development)
6. Note down your **Client ID** and **Client Secret**

## Step 2: Configure Environment Variables

Create a `.env` file in your project root with the following variables:

```bash
# QuickBooks App Credentials
QB_CLIENT_ID=your_quickbooks_client_id_here
QB_CLIENT_SECRET=your_quickbooks_client_secret_here

# QuickBooks Company ID (found in your QB company settings)
QB_COMPANY_ID=your_quickbooks_company_id_here

# QuickBooks Redirect URI
QB_REDIRECT_URI=http://localhost:5001/qb/callback

# Database Configuration
DATABASE_URI=sqlite:///inventory.db

# Flask Configuration
SECRET_KEY=your_secret_key_here
HOST=0.0.0.0
PORT=5001
DEBUG=True
```

## Step 3: Get Your Company ID

1. Log into your QuickBooks Online account
2. Go to **Settings** → **Company Settings**
3. Look for your **Company ID** (it's a number like 123456789)
4. Add this to your `.env` file as `QB_COMPANY_ID`

## Step 4: OAuth Setup (Future Enhancement)

The current implementation includes the framework for OAuth authentication. To complete the setup:

1. **Authorization URL**: The system will generate the QB authorization URL
2. **Callback Handling**: Implement the callback route to handle OAuth responses
3. **Token Storage**: Store access tokens securely for API calls

## Step 5: Test the Connection

1. Start your inventory system
2. Navigate to **QuickBooks Import** page
3. Click **Test Connection** to verify your setup
4. If successful, you'll see your company information

## Step 6: Import Data

Once connected, you can import:

### Customers
- Customer names and contact information
- Billing and shipping addresses
- Payment terms and preferences
- QuickBooks customer IDs for future sync

### Items
- Item names and descriptions
- SKUs and UPC codes
- Item categories
- Only inventory items (service items are skipped)

## API Endpoints

The following endpoints are available for QuickBooks integration:

- `GET /api/quickbooks/test-connection` - Test QB connection
- `POST /api/quickbooks/import/customers` - Import customers
- `POST /api/quickbooks/import/items` - Import items
- `GET /api/quickbooks/connect` - Initiate OAuth flow
- `POST /api/orders/{id}/sync-quickbooks` - Sync order to QB

## Important Notes

### Security
- Never commit your `.env` file to version control
- Store access tokens securely (consider using a database or encrypted storage)
- Use HTTPS in production

### Rate Limits
- QuickBooks API has rate limits (500 requests per hour for sandbox)
- The import process includes error handling for rate limit scenarios

### Data Mapping
- **Customers**: Maps QB customer data to your customer model
- **Items**: Only imports inventory items, skips service items
- **Updates**: Existing records are updated if QuickBooks ID matches
- **New Records**: Creates new records for items not found in the system

### Error Handling
- Import process includes comprehensive error handling
- Failed imports are logged with specific error messages
- Partial imports are supported (some records may succeed while others fail)

## Troubleshooting

### Common Issues

1. **"No QuickBooks access token found"**
   - Complete the OAuth flow first
   - Ensure tokens are stored properly

2. **"QuickBooks API error: 401 Unauthorized"**
   - Check your Client ID and Client Secret
   - Verify your Company ID is correct
   - Ensure your app has the necessary permissions

3. **"Connection failed"**
   - Verify your internet connection
   - Check if QuickBooks API is accessible
   - Ensure you're using the correct API endpoint (sandbox vs production)

### Debug Mode

Enable debug mode in your `.env` file to see detailed error messages:

```bash
DEBUG=True
```

## Production Considerations

1. **Environment**: Switch from sandbox to production API endpoints
2. **HTTPS**: Use HTTPS for all OAuth redirects
3. **Token Refresh**: Implement token refresh logic for long-running sessions
4. **Error Monitoring**: Set up proper error monitoring and logging
5. **Backup**: Always backup your data before large imports

## Support

For QuickBooks API issues:
- [QuickBooks API Documentation](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customer)
- [Intuit Developer Community](https://help.developer.intuit.com/)

For inventory system issues:
- Check the application logs
- Verify your database connection
- Ensure all required environment variables are set

