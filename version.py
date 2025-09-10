import json
import os
import subprocess

from datetime import datetime

# Version management for ProduceFlow Application

# Manual version - update this when you make significant changes
MANUAL_VERSION = "0.5.0"

# Version file path
VERSION_FILE = "version_info.json"

def get_git_version():
    """Get version information from git"""
    try:
        # Get current commit hash (short)
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()

        # Get current branch
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()

        # Get last commit date
        commit_date = subprocess.check_output(
            ['git', 'log', '-1', '--format=%ci'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()

        # Check if there are uncommitted changes
        status = subprocess.check_output(
            ['git', 'status', '--porcelain'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        has_uncommitted = len(status) > 0

        return {
            'commit_hash': commit_hash,
            'branch': branch,
            'commit_date': commit_date,
            'has_uncommitted': has_uncommitted,
            'source': 'git'
        }
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def get_manual_version():
    """Get manually set version information"""
    return {
        'version': MANUAL_VERSION,
        'source': 'manual',
        'last_updated': datetime.now().isoformat()
    }

def get_version_info():
    """Get comprehensive version information"""
    version_info = {
        'manual_version': MANUAL_VERSION,
        'timestamp': datetime.now().isoformat()
    }

    # Try to get git information
    git_info = get_git_version()
    if git_info:
        version_info.update(git_info)
        version_info['display_version'] = f"{MANUAL_VERSION} ({git_info['commit_hash']})"
        if git_info['has_uncommitted']:
            version_info['display_version'] += " [modified]"
    else:
        version_info['display_version'] = MANUAL_VERSION
        version_info['source'] = 'manual'

    # Add build date and display version with build time
    build_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    build_date_display = datetime.now().strftime("%b %d, %Y %I:%M %p")
    version_info['build_date'] = build_date

    # Create display version with build time
    if 'display_version' in version_info:
        version_info['display_version_with_build'] = f"v{version_info['display_version']} - {build_date_display}"
    else:
        version_info['display_version_with_build'] = f"v{MANUAL_VERSION} - {build_date_display}"

    return version_info

def save_version_info():
    """Save version information to file"""
    version_info = get_version_info()
    try:
        with open(VERSION_FILE, 'w') as f:
            json.dump(version_info, f, indent=2)
        return version_info
    except Exception as e:
        print(f"Error saving version info: {e}")
        return version_info

def load_version_info():
    """Load version information from file"""
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading version info: {e}")

    # Fallback to generating new version info
    return save_version_info()

def update_manual_version(new_version):
    """Update the manual version number"""
    global MANUAL_VERSION
    MANUAL_VERSION = new_version

    # Update the version.py file
    try:
        with open(__file__, 'r') as f:
            content = f.read()

        # Replace the MANUAL_VERSION line
        import re
        new_content = re.sub(
            r'MANUAL_VERSION = "[^"]*"',
            f'MANUAL_VERSION = "{new_version}"',
            content
        )

        with open(__file__, 'w') as f:
            f.write(new_content)

        # Save updated version info
        return save_version_info()
    except Exception as e:
        print(f"Error updating manual version: {e}")
        return None

# Initialize version info on import
VERSION_INFO = load_version_info()

# Export commonly used values
VERSION = VERSION_INFO.get('display_version', MANUAL_VERSION)
COMMIT_HASH = VERSION_INFO.get('commit_hash', 'unknown')
BRANCH = VERSION_INFO.get('branch', 'unknown')
BUILD_DATE = VERSION_INFO.get('timestamp', datetime.now().isoformat())
