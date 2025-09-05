# Version Management System

The Label Printer application includes a comprehensive version management system that displays version information in the header and provides tools for version updates.

## 🏷️ Features

### Version Display
- **Header Badge**: Shows current version in the application header
- **Version Dropdown**: Detailed version information accessible via dropdown
- **Git Integration**: Automatically detects git commit hash and branch
- **Build Information**: Displays build date and source information

### Version Management
- **Manual Updates**: Update version numbers through admin interface
- **Git Integration**: Automatically includes git commit information
- **Version API**: RESTful endpoints for version information
- **Admin Interface**: Web-based version management

## 📋 Version Information

The system displays:
- **Manual Version**: User-defined version number (e.g., 1.2.3)
- **Git Commit**: Short commit hash (e.g., 7b3b4e3)
- **Git Branch**: Current branch name (e.g., master)
- **Build Date**: When the version was last updated
- **Modification Status**: Indicates if there are uncommitted changes

### Example Display
```
v1.2.0 (7b3b4e3) [modified]
```

## 🔧 Usage

### Updating Version via Admin Interface

1. **Access Admin Panel**: Navigate to `/admin`
2. **Go to Version Management**: Click the "Version" tab
3. **Update Version**: Enter new version number (e.g., 1.2.3)
4. **Save Changes**: Click "Update Version"

### Updating Version via Script

```bash
# Update to a new version
python3 update_version.py 1.2.3

# Update to a beta version
python3 update_version.py 1.2.3-beta

# Update to a release candidate
python3 update_version.py 2.0.0-rc1
```

### Version API Endpoints

```bash
# Get version information (JSON)
curl http://localhost:5001/version

# Health check with version info
curl http://localhost:5001/health
```

## 📁 Files

### Core Files
- `version.py` - Version management module
- `update_version.py` - Command-line version update script
- `templates/admin_version.html` - Admin version management interface

### Integration
- `app.py` - Version context processor and API endpoints
- `templates/base_header.html` - Version display in header
- `templates/admin_new.html` - Admin navigation with version link

## 🎯 Version Format

The system supports semantic versioning:
- **Major.Minor.Patch**: `1.2.3`
- **Pre-release**: `1.2.3-beta`, `1.2.3-rc1`
- **Build metadata**: `1.2.3+build.123`

## 🔍 Version Information Sources

### Git Repository (Preferred)
When in a git repository, the system automatically:
- Detects current commit hash
- Shows current branch
- Indicates uncommitted changes
- Displays last commit date

### Manual Only
When not in a git repository:
- Shows only manual version number
- No git information available
- Still fully functional

## 🚀 Production Deployment

### Ubuntu VPS
The version system is fully integrated with the production deployment:
- Version information included in health checks
- Monitoring scripts display version info
- Backup scripts include version metadata

### Docker/Container
For containerized deployments:
- Version info available via `/version` endpoint
- Health checks include version information
- Environment variables can override version

## 📊 Monitoring

### Health Check Integration
```json
{
  "status": "healthy",
  "version": "1.2.0 (7b3b4e3)",
  "commit_hash": "7b3b4e3",
  "timestamp": "2025-09-05T13:47:35.826258"
}
```

### Logging
Version information is included in:
- Application startup logs
- Health check responses
- Error reports
- Monitoring dashboards

## 🔧 Configuration

### Manual Version Update
Edit `version.py`:
```python
MANUAL_VERSION = "1.2.3"  # Update this value
```

### Git Integration
The system automatically detects:
- Git repository status
- Current commit hash
- Branch information
- Uncommitted changes

## 🎨 Customization

### Header Display
Modify `templates/base_header.html` to customize:
- Version badge styling
- Dropdown content
- Version format display

### Admin Interface
Customize `templates/admin_version.html` for:
- Version update form
- Information display
- Additional metadata

## 🚨 Troubleshooting

### Common Issues

#### Version Not Updating
1. Check file permissions
2. Verify git repository status
3. Restart application after update

#### Git Information Missing
1. Ensure you're in a git repository
2. Check git command availability
3. Verify git status

#### Admin Access Issues
1. Ensure admin login
2. Check route permissions
3. Verify template inheritance

### Debug Commands
```bash
# Check version info
python3 -c "from version import VERSION_INFO; print(VERSION_INFO)"

# Test version update
python3 update_version.py 1.2.3

# Check git status
git status
git log -1 --oneline
```

## 📚 API Reference

### GET /version
Returns complete version information:
```json
{
  "version": "1.2.0 (7b3b4e3)",
  "commit_hash": "7b3b4e3",
  "branch": "master",
  "build_date": "2025-09-05T13:47:35.826258",
  "version_info": { ... }
}
```

### GET /health
Returns health status with version:
```json
{
  "status": "healthy",
  "version": "1.2.0 (7b3b4e3)",
  "commit_hash": "7b3b4e3",
  "timestamp": "2025-09-05T13:47:35.826258"
}
```

---

**Note**: The version system is designed to be lightweight and non-intrusive. It automatically adapts to your environment and provides useful information for debugging and deployment tracking.
