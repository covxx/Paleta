# Directory Structure

This document outlines the organized directory structure of the QuickBooks Label Printer application.

## Root Directory
```
label-printer/
├── app.py                    # Main Flask application
├── changelog.py             # Changelog management
├── init_database_simple.py  # Database initialization
├── qb_scheduler.py          # QuickBooks scheduler
├── requirements.txt         # Python dependencies
├── update_version.py        # Version management
├── version.py               # Version utilities
├── version_info.json        # Version information
├── .gitignore              # Git ignore rules
└── .gitkeep                # Keep uploads directory in git
```

## Organized Directories

### `/configs/` - Configuration Files
- `config.py` - Main application configuration
- `config_production.py` - Production configuration
- `gunicorn.conf.py` - Gunicorn server configuration
- `label-printer.service` - Systemd service file
- `nginx.conf` - Nginx configuration

### `/docs/` - Documentation
- `README.md` - Main project documentation
- `DESIGN_OPTIMIZATION_PLAN.md` - Design system documentation
- `QUICKBOOKS_SETUP.md` - QuickBooks integration guide
- `VPS_DEPLOYMENT_SUMMARY.md` - VPS deployment guide
- Various fix guides and implementation summaries

### `/scripts/` - Shell Scripts and Automation
- `vps_setup.sh` - VPS setup script
- `setup_ssl.sh` - SSL certificate setup
- `update_system.sh` - System update script
- `start.sh` / `start.bat` - Application startup scripts
- Various fix and diagnostic scripts

### `/tests/` - Test Files
- `test_*.py` - Various test files
- `debug_*.py` - Debug and diagnostic scripts

### `/templates/` - HTML Templates
- `base.html` - Base template with unified design
- `admin.html` - Admin panel template
- `index.html` - Main dashboard
- `quickbooks_admin.html` - QuickBooks admin interface
- Various page-specific templates

### `/static/` - Static Assets
- `/css/design-system.css` - Unified design system styles

### `/instance/` - Application Instance Data
- `inventory.db` - SQLite database (ignored by git)

### `/uploads/` - File Uploads
- `.gitkeep` - Ensures directory is tracked by git

### `/venv/` - Python Virtual Environment
- Virtual environment files (ignored by git)

## File Organization Principles

1. **Separation of Concerns**: Related files are grouped together
2. **Clear Naming**: Files have descriptive names indicating their purpose
3. **No Duplicates**: Removed duplicate and obsolete files
4. **Documentation**: All documentation is centralized in `/docs/`
5. **Configuration**: All config files are in `/configs/`
6. **Scripts**: All automation scripts are in `/scripts/`
7. **Tests**: All test files are in `/tests/`

## Maintenance

- Keep the root directory clean with only essential files
- Add new documentation to `/docs/`
- Add new scripts to `/scripts/`
- Add new tests to `/tests/`
- Add new configurations to `/configs/`
- Follow the established naming conventions
