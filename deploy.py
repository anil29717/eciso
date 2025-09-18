#!/usr/bin/env python3
"""
Deployment script for ETCISO Quiz Game
Handles production setup, database initialization, and security configuration
"""

import os
import sys
import secrets
import subprocess
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_urlsafe(32)

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        import werkzeug
        import requests
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def setup_environment():
    """Setup environment variables for production"""
    print("Setting up environment...")
    
    env_file = Path('.env')
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    try:
        secret_key = generate_secret_key()
        
        env_content = f"""# Production Environment Variables
FLASK_ENV=production
SECRET_KEY={secret_key}
DATABASE_URL=sqlite:///game.db

# Optional: External Database
# DATABASE_URL=postgresql://user:password@localhost/gamedb

# Security Settings
SSL_DISABLE=False
SESSION_COOKIE_SECURE=True

# Admin Settings (Change these!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✓ Environment file created (.env)")
        print("⚠️  Please update admin credentials in .env file!")
        return True
    except Exception as e:
        print(f"✗ Failed to create .env file: {e}")
        return False

def check_database():
    """Check database status"""
    print("Checking database...")
    
    db_file = Path('game.db')
    if db_file.exists():
        print(f"✓ Database exists ({db_file.stat().st_size} bytes)")
        return True
    else:
        print("✗ Database not found")
        print("Database will be created on first run")
        return False

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    
    directories = ['bulk_uploads', 'instance', 'logs']
    success = True
    
    for directory in directories:
        try:
            dir_path = Path(directory)
            dir_path.mkdir(exist_ok=True)
            print(f"✓ Created/verified directory: {directory}")
        except Exception as e:
            print(f"⚠️  Could not create directory '{directory}': {e}")
            print(f"   This is usually not critical for basic functionality")
            success = False
    
    return success

def check_ssl_setup():
    """Check SSL certificate setup"""
    print("Checking SSL setup...")
    
    try:
        import ssl
        print("✓ SSL module available")
        
        # Check if pyopenssl is installed for adhoc certificates
        try:
            import OpenSSL
            print("✓ PyOpenSSL available for HTTPS")
            return True
        except ImportError:
            print("⚠️  PyOpenSSL not found - installing...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyopenssl'])
            print("✓ PyOpenSSL installed")
            return True
            
    except Exception as e:
        print(f"✗ SSL setup issue: {e}")
        return False

def run_security_check():
    """Run basic security checks"""
    print("Running security checks...")
    
    issues = []
    
    # Check secret key
    if os.environ.get('SECRET_KEY') == 'dev-secret-key-change-in-production':
        issues.append("Default secret key detected - change in production!")
    
    # Check admin credentials
    if os.environ.get('ADMIN_PASSWORD') == 'admin123':
        issues.append("Default admin password detected - change immediately!")
    
    # Check file permissions (Windows-compatible)
    db_file = Path('game.db')
    if db_file.exists():
        try:
            import stat
            file_stat = db_file.stat()
            # On Windows, file permissions work differently
            if os.name == 'nt':  # Windows
                print("✓ Database file exists (Windows permissions managed by OS)")
            else:  # Unix-like systems
                if oct(file_stat.st_mode)[-3:] != '600':
                    issues.append("Database file permissions too open - should be 600")
        except Exception:
            # Skip permission check if it fails
            pass
    
    if issues:
        print("⚠️  Security issues found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✓ Basic security checks passed")
    
    return len(issues) == 0

def main():
    """Main deployment function"""
    print("=" * 50)
    print("ETCISO Quiz Game - Deployment Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("✗ Python 3.7+ required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version.split()[0]}")
    
    # Run all checks
    checks = [
        check_dependencies,
        setup_environment,
        create_directories,
        check_database,
        check_ssl_setup,
        run_security_check
    ]
    
    all_passed = True
    for check in checks:
        try:
            result = check()
            if result is False:
                all_passed = False
        except Exception as e:
            print(f"✗ Error in {check.__name__}: {e}")
            all_passed = False
        print()
    
    print("=" * 50)
    if all_passed:
        print("🎉 Deployment setup completed successfully!")
        print()
        print("Next steps:")
        print("1. Update admin credentials in .env file")
        print("2. For HTTP: python app.py")
        print("3. For HTTPS: python app_https.py")
        print("4. Access admin panel at /admin/login")
    else:
        print("⚠️  Some issues found - please resolve before deployment")
    
    print("=" * 50)

if __name__ == '__main__':
    main()