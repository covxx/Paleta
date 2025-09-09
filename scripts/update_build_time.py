#!/usr/bin/env python3
"""
Update Build Time Script for ProduceFlow
This script updates the build timestamp in version_info.json
"""

import json
import os
from datetime import datetime
from pathlib import Path

def update_build_time():
    """Update the build timestamp in version_info.json"""
    
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    version_file = project_root / "version_info.json"
    
    # Check if version_info.json exists
    if not version_file.exists():
        print(f"Error: {version_file} not found")
        return False
    
    try:
        # Read current version info
        with open(version_file, 'r') as f:
            version_info = json.load(f)
        
        # Update build timestamp
        current_time = datetime.now()
        build_date = current_time.strftime("%Y-%m-%d %H:%M:%S")
        build_date_display = current_time.strftime("%b %d, %Y %I:%M %p")
        
        # Update version info
        version_info['build_date'] = build_date
        version_info['timestamp'] = current_time.isoformat()
        
        # Update display version with build time
        if 'display_version_with_build' in version_info:
            # Extract version and commit info
            display_version = version_info.get('display_version', 'v0.5.0')
            if '(' in display_version:
                # Extract version and commit parts
                version_part = display_version.split('(')[0].strip()
                commit_part = display_version.split('(')[1].split(')')[0]
                version_info['display_version_with_build'] = f"{version_part} ({commit_part}) - {build_date_display}"
            else:
                version_info['display_version_with_build'] = f"{display_version} - {build_date_display}"
        else:
            version_info['display_version_with_build'] = f"v{version_info.get('manual_version', '0.5.0')} - {build_date_display}"
        
        # Write updated version info
        with open(version_file, 'w') as f:
            json.dump(version_info, f, indent=2)
        
        print(f"✓ Build timestamp updated: {build_date}")
        print(f"✓ Display version: {version_info['display_version_with_build']}")
        return True
        
    except Exception as e:
        print(f"Error updating build time: {e}")
        return False

if __name__ == "__main__":
    print("=== ProduceFlow Build Time Update ===")
    success = update_build_time()
    if success:
        print("Build time updated successfully!")
    else:
        print("Failed to update build time.")
        exit(1)
