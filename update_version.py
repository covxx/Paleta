#!/usr/bin/env python3
"""
Version Management Script for ProduceFlow Application
Usage: python update_version.py [new_version]
"""

import sys
import os
import subprocess
from version import update_manual_version, get_version_info, save_version_info

def print_version_info():
    """Print current version information"""
    version_info = get_version_info()
    print("📋 Current Version Information:")
    print("=" * 50)
    print(f"Manual Version: {version_info.get('manual_version', 'unknown')}")
    print(f"Display Version: {version_info.get('display_version', 'unknown')}")
    
    if version_info.get('commit_hash'):
        print(f"Git Commit: {version_info['commit_hash']}")
        print(f"Git Branch: {version_info.get('branch', 'unknown')}")
        if version_info.get('has_uncommitted'):
            print("⚠️  Warning: You have uncommitted changes")
    
    print(f"Build Date: {version_info.get('timestamp', 'unknown')}")
    print("=" * 50)

def update_version(new_version):
    """Update the manual version"""
    try:
        print(f"🔄 Updating version to: {new_version}")
        result = update_manual_version(new_version)
        
        if result:
            print("✅ Version updated successfully!")
            print_version_info()
            
            # Optionally commit the version change
            try:
                response = input("\n📝 Would you like to commit this version change? (y/N): ")
                if response.lower() in ['y', 'yes']:
                    commit_message = f"Bump version to {new_version}"
                    subprocess.run(['git', 'add', 'version.py'], check=True)
                    subprocess.run(['git', 'commit', '-m', commit_message], check=True)
                    print("✅ Version change committed to git")
            except subprocess.CalledProcessError:
                print("⚠️  Could not commit to git (not a git repository or git not available)")
            except KeyboardInterrupt:
                print("\n⏹️  Skipped git commit")
        else:
            print("❌ Failed to update version")
            return False
            
    except Exception as e:
        print(f"❌ Error updating version: {e}")
        return False
    
    return True

def get_git_status():
    """Get git status information"""
    try:
        # Check if we're in a git repository
        subprocess.run(['git', 'status'], check=True, capture_output=True)
        
        # Get current branch
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()
        
        # Get last commit
        last_commit = subprocess.check_output(['git', 'log', '-1', '--oneline']).decode().strip()
        
        # Check for uncommitted changes
        status = subprocess.check_output(['git', 'status', '--porcelain']).decode().strip()
        has_changes = len(status) > 0
        
        print("🔍 Git Status:")
        print(f"  Branch: {branch}")
        print(f"  Last Commit: {last_commit}")
        if has_changes:
            print("  ⚠️  Uncommitted changes detected")
        else:
            print("  ✅ Working directory clean")
            
    except subprocess.CalledProcessError:
        print("⚠️  Not in a git repository or git not available")
    except Exception as e:
        print(f"⚠️  Error checking git status: {e}")

def main():
    """Main function"""
    print("🏷️  ProduceFlow Version Manager")
    print("=" * 50)
    
    # Show current version info
    print_version_info()
    print()
    
    # Show git status
    get_git_status()
    print()
    
    # Check if new version provided
    if len(sys.argv) > 1:
        new_version = sys.argv[1]
        
        # Validate version format (basic check)
        if not new_version.replace('.', '').replace('-', '').replace('_', '').isalnum():
            print("❌ Invalid version format. Use format like: 1.2.3, 1.2.3-beta, etc.")
            sys.exit(1)
        
        update_version(new_version)
    else:
        print("💡 Usage:")
        print("  python update_version.py [new_version]")
        print()
        print("📝 Examples:")
        print("  python update_version.py 1.2.3")
        print("  python update_version.py 1.2.3-beta")
        print("  python update_version.py 2.0.0-rc1")
        print()
        print("🔧 To update version, run:")
        print("  python update_version.py <new_version>")

if __name__ == "__main__":
    main()
