#!/usr/bin/env python3

"""
Health check script for the School Management System
Tests basic functionality and database connectivity
"""

import os
import sys
import time
from urllib.parse import urlparse

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

def check_environment():
    """Check if required environment variables are set"""
    print("🔧 Checking environment variables...")
    
    required_vars = ['DATABASE_URL', 'SESSION_SECRET']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def check_database_connection():
    """Test database connectivity"""
    print("🗄️ Checking database connection...")
    
    try:
        # Import here to avoid issues if dependencies aren't installed
        from sqlalchemy import create_engine, text
        
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not set")
            return False
            
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print("✅ Database connection successful")
        return True
    except ImportError:
        print("⚠️ SQLAlchemy not installed, skipping database check")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def check_web_app(url):
    """Test web application response"""
    print(f"🌐 Checking web app at {url}...")
    
    if not HAS_REQUESTS:
        print("⚠️ requests module not installed, skipping web app check")
        print("   Install with: pip install requests")
        return True
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            print("✅ Web app responding successfully")
            return True
        else:
            print(f"⚠️ Web app returned status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Web app check failed: {str(e)}")
        return False

def main():
    """Run all health checks"""
    print("🏥 School Management System Health Check")
    print("=" * 45)
    print()
    
    checks_passed = 0
    total_checks = 0
    
    # Check environment
    total_checks += 1
    if check_environment():
        checks_passed += 1
    print()
    
    # Check database
    total_checks += 1
    if check_database_connection():
        checks_passed += 1
    print()
    
    # Check web app if URL provided
    if len(sys.argv) > 1:
        url = sys.argv[1]
        total_checks += 1
        if check_web_app(url):
            checks_passed += 1
        print()
    
    # Summary
    print("📊 Health Check Summary")
    print("=" * 23)
    print(f"Checks passed: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("🎉 All checks passed! Your app is healthy.")
        sys.exit(0)
    else:
        print("⚠️ Some checks failed. Please review the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()