# Changelog management for ProduceFlow Application
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# Changelog file path
CHANGELOG_FILE = "changelog.json"

# Default changelog structure
DEFAULT_CHANGELOG = {
    "0.5.0": {
        "date": "2025-09-08",
        "type": "minor",
        "title": "ProduceFlow - Unified Design & Interactive VPS Setup",
        "description": "Complete UI/UX overhaul with unified design system and interactive VPS deployment",
        "changes": [
            {
                "type": "feature",
                "title": "Interactive VPS Setup",
                "description": "Fully interactive VPS deployment script with domain configuration and SSL setup"
            },
            {
                "type": "feature",
                "title": "Unified Design System",
                "description": "Complete UI/UX overhaul with responsive design, dark mode, and consistent styling"
            },
            {
                "type": "feature",
                "title": "Enhanced Order Management",
                "description": "Improved order interface with customer avatars, status indicators, and contact info"
            },
            {
                "type": "feature",
                "title": "Domain Configuration",
                "description": "Interactive domain setup with validation, DNS guidance, and Nginx configuration"
            },
            {
                "type": "improvement",
                "title": "Application Rebranding",
                "description": "Renamed from 'QuickBooks Label Printer' to 'ProduceFlow' throughout the application"
            },
            {
                "type": "improvement",
                "title": "Responsive Navigation",
                "description": "Streamlined navigation with mobile-optimized design and consistent header"
            },
            {
                "type": "improvement",
                "title": "Template System Overhaul",
                "description": "All templates updated to use unified base template and design system"
            },
            {
                "type": "security",
                "title": "Production Security",
                "description": "Enhanced security headers, rate limiting, and production-ready configurations"
            }
        ],
        "issues": [
            {
                "id": "UI-001",
                "title": "Implement unified design system",
                "status": "completed",
                "priority": "high"
            },
            {
                "id": "VPS-001",
                "title": "Create interactive VPS setup",
                "status": "completed",
                "priority": "high"
            },
            {
                "id": "DOMAIN-001",
                "title": "Add domain configuration",
                "status": "completed",
                "priority": "medium"
            },
            {
                "id": "BRAND-001",
                "title": "Rebrand to ProduceFlow",
                "status": "completed",
                "priority": "medium"
            }
        ],
        "breaking_changes": [],
        "deprecations": [
            "Old template files (_new.html variants) removed during cleanup"
        ],
        "contributors": ["Development Team"]
    },
    "1.2.0": {
        "date": "2025-09-05",
        "type": "minor",
        "title": "Ubuntu VPS Optimization & Version Management",
        "description": "Major performance improvements and production deployment features",
        "changes": [
            {
                "type": "feature",
                "title": "Ubuntu VPS Deployment",
                "description": "Complete deployment system optimized for 4-core VPS with Gunicorn, Nginx, and Redis"
            },
            {
                "type": "feature", 
                "title": "Version Management System",
                "description": "Comprehensive version tracking with git integration and admin interface"
            },
            {
                "type": "feature",
                "title": "Production Monitoring",
                "description": "Health checks, logging, and monitoring scripts for production environment"
            },
            {
                "type": "improvement",
                "title": "Performance Optimization",
                "description": "Database connection pooling, Redis caching, and multi-worker configuration"
            },
            {
                "type": "security",
                "title": "Security Enhancements",
                "description": "Firewall configuration, fail2ban, and security headers"
            }
        ],
        "issues": [
            {
                "id": "VPS-001",
                "title": "Optimize for 4-core Ubuntu VPS",
                "status": "completed",
                "priority": "high"
            },
            {
                "id": "VPS-002", 
                "title": "Implement version management",
                "status": "completed",
                "priority": "medium"
            },
            {
                "id": "VPS-003",
                "title": "Add production monitoring",
                "status": "completed",
                "priority": "medium"
            }
        ],
        "breaking_changes": [],
        "deprecations": [],
        "contributors": ["Development Team"]
    },
    "1.1.0": {
        "date": "2025-08-28",
        "type": "minor",
        "title": "Order Management & QuickBooks Integration",
        "description": "Enhanced order processing and QuickBooks connectivity",
        "changes": [
            {
                "type": "feature",
                "title": "Order Management System",
                "description": "Complete order entry, processing, and fulfillment workflow"
            },
            {
                "type": "feature",
                "title": "QuickBooks Integration",
                "description": "Import customers and products from QuickBooks Online"
            },
            {
                "type": "feature",
                "title": "Customer Management",
                "description": "Customer database with contact information and order history"
            },
            {
                "type": "improvement",
                "title": "Label Designer",
                "description": "Enhanced label design with custom templates and barcode generation"
            }
        ],
        "issues": [
            {
                "id": "QB-001",
                "title": "QuickBooks API integration",
                "status": "completed",
                "priority": "high"
            },
            {
                "id": "ORD-001",
                "title": "Order entry system",
                "status": "completed",
                "priority": "high"
            }
        ],
        "breaking_changes": [],
        "deprecations": [],
        "contributors": ["Development Team"]
    },
    "1.0.0": {
        "date": "2025-08-15",
        "type": "major",
        "title": "Initial Release",
        "description": "Core inventory management and label printing functionality",
        "changes": [
            {
                "type": "feature",
                "title": "Inventory Management",
                "description": "Complete inventory tracking with items, lots, and vendors"
            },
            {
                "type": "feature",
                "title": "Label Printing",
                "description": "ZPL label generation with barcodes and QR codes"
            },
            {
                "type": "feature",
                "title": "Receiving System",
                "description": "Product receiving workflow with lot code generation"
            },
            {
                "type": "feature",
                "title": "Admin Panel",
                "description": "Administrative interface for system management"
            }
        ],
        "issues": [
            {
                "id": "INV-001",
                "title": "Core inventory system",
                "status": "completed",
                "priority": "high"
            },
            {
                "id": "LAB-001",
                "title": "Label printing system",
                "status": "completed",
                "priority": "high"
            }
        ],
        "breaking_changes": [],
        "deprecations": [],
        "contributors": ["Development Team"]
    }
}

def load_changelog() -> Dict:
    """Load changelog from file or return default"""
    try:
        if os.path.exists(CHANGELOG_FILE):
            with open(CHANGELOG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading changelog: {e}")
    
    return DEFAULT_CHANGELOG

def save_changelog(changelog: Dict) -> bool:
    """Save changelog to file"""
    try:
        with open(CHANGELOG_FILE, 'w') as f:
            json.dump(changelog, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving changelog: {e}")
        return False

def get_version_changelog(version: str) -> Optional[Dict]:
    """Get changelog for specific version"""
    changelog = load_changelog()
    return changelog.get(version)

def get_latest_changelog() -> Optional[Dict]:
    """Get changelog for latest version"""
    changelog = load_changelog()
    if not changelog:
        return None
    
    # Sort versions and get latest
    versions = sorted(changelog.keys(), key=lambda x: [int(i) for i in x.split('.')], reverse=True)
    return changelog.get(versions[0]) if versions else None

def get_all_versions() -> List[str]:
    """Get all version numbers sorted by version"""
    changelog = load_changelog()
    if not changelog:
        return []
    
    # Sort versions in descending order
    return sorted(changelog.keys(), key=lambda x: [int(i) for i in x.split('.')], reverse=True)

def add_version_changelog(version: str, changelog_data: Dict) -> bool:
    """Add or update changelog for a version"""
    changelog = load_changelog()
    changelog[version] = changelog_data
    return save_changelog(changelog)

def get_change_types() -> List[str]:
    """Get available change types"""
    return ["feature", "improvement", "bugfix", "security", "deprecation", "breaking"]

def get_issue_statuses() -> List[str]:
    """Get available issue statuses"""
    return ["open", "in_progress", "completed", "cancelled", "on_hold"]

def get_issue_priorities() -> List[str]:
    """Get available issue priorities"""
    return ["low", "medium", "high", "critical"]

def create_version_template(version: str, version_type: str = "patch") -> Dict:
    """Create a template for a new version changelog"""
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": version_type,
        "title": f"Version {version}",
        "description": "Description of changes in this version",
        "changes": [],
        "issues": [],
        "breaking_changes": [],
        "deprecations": [],
        "contributors": []
    }

def get_changelog_summary() -> Dict:
    """Get summary of all changelog data"""
    changelog = load_changelog()
    versions = get_all_versions()
    
    summary = {
        "total_versions": len(versions),
        "latest_version": versions[0] if versions else None,
        "version_types": {},
        "total_changes": 0,
        "total_issues": 0,
        "recent_versions": versions[:5] if versions else []
    }
    
    # Count by type
    for version, data in changelog.items():
        version_type = data.get("type", "unknown")
        summary["version_types"][version_type] = summary["version_types"].get(version_type, 0) + 1
        
        # Count changes and issues
        summary["total_changes"] += len(data.get("changes", []))
        summary["total_issues"] += len(data.get("issues", []))
    
    return summary

# Initialize changelog on import
CHANGELOG_DATA = load_changelog()
