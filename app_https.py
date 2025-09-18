#!/usr/bin/env python3
"""
HTTPS version of the Flask app for camera access on Android browsers
"""

from app import app
import os

if __name__ == '__main__':
    print("Starting Flask app with HTTPS...")
    print("===============================\n")
    
    # Check if pyopenssl is installed
    try:
        import OpenSSL
        print("✓ pyopenssl is installed")
    except ImportError:
        print("✗ pyopenssl not found. Installing...")
        os.system('pip install pyopenssl')
        print("✓ pyopenssl installed")
    
    print("\n🔒 Starting HTTPS server...")
    print("📱 Camera access will work on Android browsers")
    print("🌐 Access your app at: https://localhost:5000")
    print("⚠️  Browser will show security warning - click 'Advanced' -> 'Proceed to localhost'\n")
    
    # Run Flask app with HTTPS using adhoc SSL context
    # This generates self-signed certificates on-the-fly
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000,
        ssl_context='adhoc'  # This creates self-signed certificates automatically
    )