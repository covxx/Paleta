#!/usr/bin/env python3
"""
Changelog Management Script for Label Printer Application
Usage: python3 manage_changelog.py [command] [options]
"""

import sys
import json
import os
from datetime import datetime
from changelog import (
    load_changelog, save_changelog, add_version_changelog,
    get_all_versions, create_version_template, get_change_types,
    get_issue_statuses, get_issue_priorities
)

def print_help():
    """Print help information"""
    print("🏷️  Changelog Management Tool")
    print("=" * 50)
    print("Commands:")
    print("  list                    - List all versions")
    print("  show <version>          - Show changelog for specific version")
    print("  add <version>           - Add new version changelog")
    print("  edit <version>          - Edit existing version changelog")
    print("  summary                 - Show changelog summary")
    print("  help                    - Show this help")
    print()
    print("Examples:")
    print("  python3 manage_changelog.py list")
    print("  python3 manage_changelog.py show 1.2.0")
    print("  python3 manage_changelog.py add 1.3.0")
    print("  python3 manage_changelog.py summary")

def list_versions():
    """List all versions"""
    versions = get_all_versions()
    changelog = load_changelog()
    
    print("📋 All Versions:")
    print("=" * 50)
    
    if not versions:
        print("No versions found.")
        return
    
    for version in versions:
        version_data = changelog[version]
        print(f"v{version}")
        print(f"  Type: {version_data.get('type', 'unknown').title()}")
        print(f"  Date: {version_data.get('date', 'unknown')}")
        print(f"  Title: {version_data.get('title', 'No title')}")
        print(f"  Changes: {len(version_data.get('changes', []))}")
        print(f"  Issues: {len(version_data.get('issues', []))}")
        print()

def show_version(version):
    """Show changelog for specific version"""
    changelog = load_changelog()
    
    if version not in changelog:
        print(f"❌ Version {version} not found.")
        return
    
    version_data = changelog[version]
    
    print(f"📋 Version {version} Changelog:")
    print("=" * 50)
    print(f"Type: {version_data.get('type', 'unknown').title()}")
    print(f"Date: {version_data.get('date', 'unknown')}")
    print(f"Title: {version_data.get('title', 'No title')}")
    print(f"Description: {version_data.get('description', 'No description')}")
    print()
    
    # Changes
    changes = version_data.get('changes', [])
    if changes:
        print(f"📝 Changes ({len(changes)}):")
        for i, change in enumerate(changes, 1):
            print(f"  {i}. [{change.get('type', 'unknown').title()}] {change.get('title', 'No title')}")
            print(f"     {change.get('description', 'No description')}")
        print()
    
    # Issues
    issues = version_data.get('issues', [])
    if issues:
        print(f"🐛 Issues ({len(issues)}):")
        for issue in issues:
            print(f"  {issue.get('id', 'N/A')}: {issue.get('title', 'No title')}")
            print(f"    Status: {issue.get('status', 'unknown')}")
            print(f"    Priority: {issue.get('priority', 'unknown')}")
        print()
    
    # Breaking changes
    breaking = version_data.get('breaking_changes', [])
    if breaking:
        print(f"⚠️  Breaking Changes ({len(breaking)}):")
        for breaking_change in breaking:
            print(f"  - {breaking_change.get('title', 'No title')}")
        print()
    
    # Contributors
    contributors = version_data.get('contributors', [])
    if contributors:
        print(f"👥 Contributors: {', '.join(contributors)}")

def add_version_interactive(version):
    """Add new version changelog interactively"""
    print(f"➕ Adding new version: {version}")
    print("=" * 50)
    
    # Get version type
    print("Version types:", ", ".join(get_change_types()))
    version_type = input("Version type (major/minor/patch): ").strip().lower()
    if version_type not in ['major', 'minor', 'patch', 'beta', 'rc']:
        version_type = 'patch'
    
    # Get title
    title = input("Version title: ").strip()
    if not title:
        title = f"Version {version}"
    
    # Get description
    description = input("Version description: ").strip()
    if not description:
        description = "Description of changes in this version"
    
    # Create template
    version_data = create_version_template(version, version_type)
    version_data['title'] = title
    version_data['description'] = description
    
    # Add changes
    print("\n📝 Adding changes (press Enter with empty title to finish):")
    while True:
        change_title = input("Change title: ").strip()
        if not change_title:
            break
        
        print("Change types:", ", ".join(get_change_types()))
        change_type = input("Change type: ").strip().lower()
        if change_type not in get_change_types():
            change_type = 'improvement'
        
        change_description = input("Change description: ").strip()
        if not change_description:
            change_description = "No description provided"
        
        version_data['changes'].append({
            'type': change_type,
            'title': change_title,
            'description': change_description
        })
    
    # Add issues
    print("\n🐛 Adding issues (press Enter with empty ID to finish):")
    while True:
        issue_id = input("Issue ID: ").strip()
        if not issue_id:
            break
        
        issue_title = input("Issue title: ").strip()
        if not issue_title:
            continue
        
        print("Issue statuses:", ", ".join(get_issue_statuses()))
        issue_status = input("Issue status: ").strip().lower()
        if issue_status not in get_issue_statuses():
            issue_status = 'open'
        
        print("Issue priorities:", ", ".join(get_issue_priorities()))
        issue_priority = input("Issue priority: ").strip().lower()
        if issue_priority not in get_issue_priorities():
            issue_priority = 'medium'
        
        version_data['issues'].append({
            'id': issue_id,
            'title': issue_title,
            'status': issue_status,
            'priority': issue_priority
        })
    
    # Save
    if add_version_changelog(version, version_data):
        print(f"\n✅ Version {version} added successfully!")
        show_version(version)
    else:
        print(f"\n❌ Failed to add version {version}")

def show_summary():
    """Show changelog summary"""
    from changelog import get_changelog_summary
    
    summary = get_changelog_summary()
    
    print("📊 Changelog Summary:")
    print("=" * 50)
    print(f"Total Versions: {summary['total_versions']}")
    print(f"Latest Version: {summary['latest_version']}")
    print(f"Total Changes: {summary['total_changes']}")
    print(f"Total Issues: {summary['total_issues']}")
    print()
    
    print("Version Types:")
    for version_type, count in summary['version_types'].items():
        print(f"  {version_type.title()}: {count}")
    print()
    
    print("Recent Versions:")
    for version in summary['recent_versions']:
        print(f"  v{version}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'help':
        print_help()
    elif command == 'list':
        list_versions()
    elif command == 'show':
        if len(sys.argv) < 3:
            print("❌ Please specify a version number.")
            return
        show_version(sys.argv[2])
    elif command == 'add':
        if len(sys.argv) < 3:
            print("❌ Please specify a version number.")
            return
        add_version_interactive(sys.argv[2])
    elif command == 'summary':
        show_summary()
    else:
        print(f"❌ Unknown command: {command}")
        print_help()

if __name__ == "__main__":
    main()
