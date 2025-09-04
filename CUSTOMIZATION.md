# Customization Guide

## Company Information

To customize the company information that appears on your labels, edit the `config.py` file:

```python
# Company Information (for labels)
COMPANY_NAME = "YOUR COMPANY NAME"
COMPANY_ADDRESS = "123 Business Street, City, ST 12345"
```

Replace the placeholder values with your actual company information.

## Label Types

The system now supports two types of labels:

### 1. Standard Label (Palumbo-style)
- **4x2 inch label format** optimized for Zebra printers
- Company header with name and address
- Product description with quantity format: "12 / 8 oz Whole White"
- Item code (last 6 digits of GTIN) and LOT number
- GS1-128 barcode with human-readable data
- QR code for additional scanning
- Tight margins (0.1 inch) for maximum content space

### 2. PTI FSMA Label
- PTI FSMA compliance header
- Product information (name, GTIN, LOT)
- Pack date and expiry information
- GS1-128 barcode (PTI requirement)
- Professional format for food safety compliance

## Label Dimensions

You can customize label dimensions in `config.py`:

```python
# Label Configuration
LABEL_WIDTH = 4.0    # Label width in inches (4 inches)
LABEL_HEIGHT = 2.0   # Label height in inches (2 inches)
LABEL_MARGIN = 0.1   # Label margin in inches (tight margins for 4x2)
```

**Current Configuration:**
- **Width**: 4.0 inches (standard Zebra label width)
- **Height**: 2.0 inches (standard Zebra label height)
- **Margins**: 0.1 inches (tight margins for maximum content)

## LOT Code Format

Customize the LOT code generation format:

```python
# LOT Code Configuration
LOT_PREFIX = 'LOT'   # Prefix for LOT codes
LOT_TIMESTAMP_FORMAT = '%Y%m%d%H%M'  # Timestamp format
LOT_RANDOM_SUFFIX_LENGTH = 4  # Length of random suffix
```

## Barcode Configuration

Adjust QR code and barcode settings:

```python
# QR Code Configuration
QR_VERSION = 1       # QR code version (1-40)
QR_BOX_SIZE = 2     # QR code box size
QR_BORDER = 1       # QR code border width
```

## Example Customizations

### Food Company Example
```python
COMPANY_NAME = "Fresh Foods Inc."
COMPANY_ADDRESS = "456 Farm Road, Organic Valley, CA 90210"
LOT_PREFIX = 'FF'
```

### Manufacturing Company Example
```python
COMPANY_NAME = "Quality Manufacturing Co."
COMPANY_ADDRESS = "789 Industrial Blvd, Manufacturing City, TX 75001"
LOT_PREFIX = 'QM'
```

## Advanced Customization

For more advanced label customization, you can modify the label generation functions in `app.py`:

- `generate_palumbo_style_label()` - Standard label format
- `generate_pti_fsma_label()` - PTI FSMA compliant format

## Font and Styling

The labels use standard fonts:
- Helvetica-Bold for headers
- Helvetica for body text
- Adjustable font sizes for different sections

## Barcode Standards

The system generates GS1-128 barcodes with:
- (01) - GTIN (Global Trade Item Number)
- (15) - Production Date (YYMMDD format)
- (10) - LOT/Batch Number

This format is compliant with:
- PTI (Produce Traceability Initiative)
- FSMA (Food Safety Modernization Act)
- GS1 standards for supply chain tracking
