# Inventory Management System

A web-based inventory system for creating LOT codes and GTIN Zebra labels that can be accessed from multiple PCs on your network.

## Features

- **Item Management**: Create and manage inventory items with GTIN codes
- **LOT Code Generation**: Automatically generate unique LOT codes for items
- **Zebra Label Creation**: Generate PDF labels with QR codes for printing
- **Multi-PC Access**: Web-based interface accessible from any device on your network
- **Search & Filter**: Quick search through items and LOT codes
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## System Requirements

- Python 3.7 or higher
- Network access for multi-PC connectivity
- Web browser (Chrome, Firefox, Safari, Edge)

## Installation

### Option 1: Automatic Setup (Recommended)

1. **Clone or download** the project files to your computer

2. **Run the startup script**:
   ```bash
   # On Mac/Linux:
   ./start.sh
   
   # On Windows:
   start.bat
   
   # Or with Python:
   python start.py
   ```

   The script will automatically:
   - Create a virtual environment
   - Install all dependencies
   - Start the application

### Option 2: Manual Setup

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   ```

2. **Activate virtual environment**:
   ```bash
   # On Mac/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate.bat
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

### Access the System

Once running, access the system at:
- On the same computer: `http://localhost:5000`
- From other PCs on the network: `http://[YOUR_COMPUTER_IP]:5000`

## Virtual Environment Management

The project uses a Python virtual environment to isolate dependencies.

### Activating the Virtual Environment

```bash
# On Mac/Linux:
./activate.sh

# On Windows:
activate.bat

# Manual activation:
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate.bat  # Windows
```

### Deactivating the Virtual Environment

```bash
# On Mac/Linux:
./deactivate.sh

# Manual deactivation:
deactivate
```

### Working with the Virtual Environment

- **Install packages**: `pip install package_name`
- **List packages**: `pip list`
- **Update packages**: `pip install --upgrade package_name`
- **Remove packages**: `pip uninstall package_name`

### Recreating the Virtual Environment

If you need to recreate the virtual environment:

```bash
# Remove old environment
rm -rf venv  # Mac/Linux
rmdir /s venv  # Windows

# Create new environment
python3 -m venv venv

# Activate and install dependencies
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

## Usage

### Creating Items

1. Go to the "Create New" tab
2. Fill in the item details:
   - **Item Name**: Descriptive name for the item
   - **GTIN**: 14-digit Global Trade Item Number
   - **Description**: Optional description
3. Click "Create Item"

### Creating LOT Codes

1. Go to the "Create New" tab
2. Select an existing item from the dropdown
3. Enter quantity and expiry date (optional)
4. Click "Create LOT Code"
5. The system will generate a unique LOT code

### Generating Labels

1. Go to the "LOT Codes" tab
2. Find the LOT code you want to label
3. Click the "Label" button
4. A PDF label will download with:
   - Item information
   - GTIN code
   - LOT code
   - Quantity and expiry date
   - QR code for scanning

### Multi-PC Access

To access the system from other computers on your network:

1. **Find your computer's IP address**:
   - Windows: Run `ipconfig` in Command Prompt
   - Mac/Linux: Run `ifconfig` or `ip addr` in Terminal

2. **Access from other PCs**:
   - Open a web browser
   - Navigate to `http://[YOUR_IP_ADDRESS]:5000`
   - Example: `http://192.168.1.100:5000`

## File Structure

```
inventory-system/
├── app.py                 # Main Flask application
├── config.py              # Configuration file
├── requirements.txt       # Python dependencies
├── requirements-lock.txt  # Exact package versions
├── start.py              # Python startup script
├── start.sh              # Mac/Linux startup script
├── start.bat             # Windows startup script
├── activate.sh            # Mac/Linux virtual env activation
├── activate.bat           # Windows virtual env activation
├── deactivate.sh          # Virtual env deactivation
├── demo_data.py           # Sample data generator
├── templates/             # HTML templates
│   └── index.html        # Main web interface
├── venv/                  # Virtual environment (created automatically)
├── inventory.db           # SQLite database (created automatically)
├── README.md             # This file
└── CUSTOMIZATION.md      # Label customization guide
```

## Database

The system uses SQLite for data storage. The database file (`inventory.db`) is created automatically when you first run the application.

### Tables

- **items**: Stores item information (name, GTIN, description)
- **lots**: Stores LOT codes with references to items

## Customization

### Changing Port

To change the port number, edit `app.py`:

```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

Change `port=5000` to your desired port number.

### Label Format

To customize the label format, modify the `generate_label` function in `app.py`. The current format includes:

- Item name
- GTIN code
- LOT code
- Quantity
- Expiry date
- QR code

### LOT Code Format

The default LOT code format is: `LOT[ITEM_ID][TIMESTAMP][RANDOM_SUFFIX]`

To change this, modify the `generate_lot_code` function in `app.py`.

## Security Notes

- The application runs with `debug=True` for development
- For production use, change the secret key in `app.py`
- The system binds to `0.0.0.0` to allow network access
- Consider implementing authentication for production environments

## Troubleshooting

### Port Already in Use

If you get a "port already in use" error:

1. Change the port number in `app.py`
2. Or stop other services using port 5000

### Network Access Issues

1. **Check firewall settings** on your computer
2. **Verify network connectivity** between PCs
3. **Check IP address** - make sure you're using the correct IP

### Database Issues

If you encounter database errors:

1. Delete the `inventory.db` file
2. Restart the application
3. The database will be recreated automatically

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure Python version compatibility

## License

This project is provided as-is for educational and business use.
