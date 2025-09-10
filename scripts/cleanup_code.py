"""
Code Cleanup Script

Cleans up and organizes the codebase for better maintainability.
"""

import os
import re
from pathlib import Path

def cleanup_python_files():
    """Clean up Python files"""
    python_files = []

    # Find all Python files
    for root, dirs, files in os.walk('.'):
        # Skip virtual environment and cache directories
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]

        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    print(f"Found {len(python_files)} Python files to clean up")

    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Remove trailing whitespace
            content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

            # Ensure file ends with newline
            if content and not content.endswith('\n'):
                content += '\n'

            # Remove duplicate blank lines (more than 2 consecutive)
            content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)

            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Cleaned up: {file_path}")

        except Exception as e:
            print(f"Error cleaning {file_path}: {e}")

def organize_imports():
    """Organize imports in Python files"""
    python_files = []

    # Find all Python files
    for root, dirs, files in os.walk('.'):
        # Skip virtual environment and cache directories
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]

        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Find import sections
            import_lines = []
            from_import_lines = []
            other_lines = []

            in_imports = True

            for line in lines:
                stripped = line.strip()

                if in_imports and (stripped.startswith('import ') or stripped.startswith('from ')):
                    if stripped.startswith('import '):
                        import_lines.append(line)
                    else:
                        from_import_lines.append(line)
                else:
                    if stripped and not stripped.startswith('#'):
                        in_imports = False
                    other_lines.append(line)

            # Sort imports
            import_lines.sort()
            from_import_lines.sort()

            # Reconstruct file
            new_content = []

            # Add imports
            if import_lines:
                new_content.extend(import_lines)
                if from_import_lines:
                    new_content.append('\n')

            if from_import_lines:
                new_content.extend(from_import_lines)
                if other_lines:
                    new_content.append('\n')

            # Add other content
            new_content.extend(other_lines)

            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_content)

            print(f"Organized imports in: {file_path}")

        except Exception as e:
            print(f"Error organizing imports in {file_path}: {e}")

def create_gitignore():
    """Create or update .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Uploads
uploads/
temp/

# Configuration
.env
config_local.py

# Testing
.coverage
.pytest_cache/
htmlcov/

# Documentation
docs/_build/

# Backup files
*.bak
*.backup
*.old

# Temporary files
*.tmp
*.temp
"""

    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)

    print("Created/updated .gitignore file")

def create_requirements_dev():
    """Create development requirements file"""
    dev_requirements = """# Development Dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0
pre-commit>=2.20.0

# Testing
pytest-flask>=1.2.0
pytest-mock>=3.8.0

# Code Quality
isort>=5.10.0
bandit>=1.7.0

# Documentation
sphinx>=5.0.0
sphinx-rtd-theme>=1.0.0
"""

    with open('requirements-dev.txt', 'w') as f:
        f.write(dev_requirements)

    print("Created requirements-dev.txt file")

def create_pre_commit_config():
    """Create pre-commit configuration"""
    pre_commit_config = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 22.12.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
"""

    with open('.pre-commit-config.yaml', 'w') as f:
        f.write(pre_commit_config)

    print("Created .pre-commit-config.yaml file")

def create_makefile():
    """Create Makefile for common tasks"""
    makefile_content = """# Makefile for ProduceFlow Label Printer

.PHONY: help install install-dev test lint format clean run deploy

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test:  ## Run tests
	pytest tests/ -v --cov=app --cov-report=html

lint:  ## Run linting
	flake8 app.py services/ utils/ middleware/ api/
	black --check app.py services/ utils/ middleware/ api/
	isort --check-only app.py services/ utils/ middleware/ api/

format:  ## Format code
	black app.py services/ utils/ middleware/ api/
	isort app.py services/ utils/ middleware/ api/

clean:  ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage

run:  ## Run the application
	python app.py

run-dev:  ## Run the application in development mode
	export FLASK_ENV=development
	export FLASK_DEBUG=True
	python app.py

deploy:  ## Deploy to production
	git push origin master
	ssh user@server 'cd /opt/label-printer && git pull && sudo systemctl restart label-printer'

backup:  ## Backup database
	python scripts/backup_database.py

migrate:  ## Run database migrations
	python scripts/migrate_database.py

optimize:  ## Optimize database
	python scripts/optimize_database.py

setup: install-dev  ## Setup development environment
	pre-commit install
	python scripts/optimize_database.py
"""

    with open('Makefile', 'w') as f:
        f.write(makefile_content)

    print("Created Makefile")

def main():
    """Main cleanup function"""
    print("Starting code cleanup and organization...")

    print("\n1. Cleaning up Python files...")
    cleanup_python_files()

    print("\n2. Organizing imports...")
    organize_imports()

    print("\n3. Creating .gitignore...")
    create_gitignore()

    print("\n4. Creating development requirements...")
    create_requirements_dev()

    print("\n5. Creating pre-commit configuration...")
    create_pre_commit_config()

    print("\n6. Creating Makefile...")
    create_makefile()

    print("\n✅ Code cleanup and organization completed!")
    print("\nNext steps:")
    print("1. Run 'make install-dev' to install development dependencies")
    print("2. Run 'make format' to format all code")
    print("3. Run 'make test' to run tests")
    print("4. Run 'make lint' to check code quality")

if __name__ == "__main__":
    main()
