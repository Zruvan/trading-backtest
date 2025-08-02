"""Verify setup for trading backtest system."""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    else:
        print("✅ Python version OK")
        return True

def check_packages():
    """Check required packages."""
    required_packages = [
        'pandas', 'numpy', 'sqlalchemy', 'requests', 
        'matplotlib', 'reportlab', 'pytest'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def check_files():
    """Check required files exist."""
    required_files = [
        'requirements.txt',
        'setup.py',
        '.env.example',
        'config/constants.py',
        'config/settings.example.py',
        'data/models.py',
        'data/database.py',
        'strategies/base.py',
        'backtest/performance.py',
        'scripts/setup_db.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def check_config():
    """Check configuration."""
    env_file = project_root / '.env'
    settings_file = project_root / 'config' / 'settings.py'
    
    print("\n📋 Configuration Status:")
    
    if env_file.exists():
        print("✅ .env file exists")
        # Check if API key is set
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if 'FMP_API_KEY=your_fmp_api_key_here' in content:
                    print("⚠️  FMP API key not configured (using placeholder)")
                elif 'FMP_API_KEY=' in content:
                    print("✅ FMP API key configured")
                else:
                    print("❌ FMP API key not found in .env")
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
    else:
        print("❌ .env file missing - copy from .env.example")
    
    if settings_file.exists():
        print("✅ settings.py file exists")
    else:
        print("❌ config/settings.py missing - copy from config/settings.example.py")

def check_database():
    """Test database connection."""
    print("\n🗄️  Database Status:")
    
    try:
        # Try to import and test database
        from data.database import init_database
        
        # Use SQLite for testing
        DATABASE_URL = "sqlite:///test_trading_backtest.db"
        db_manager = init_database(DATABASE_URL)
        
        if db_manager.health_check():
            print("✅ Database connection successful (SQLite)")
            
            # Close database connections before cleanup
            db_manager.close()
            
            # Clean up test database
            import time
            time.sleep(0.1)  # Brief pause to ensure connections are closed
            test_db = project_root / "test_trading_backtest.db"
            if test_db.exists():
                try:
                    test_db.unlink()
                except OSError:
                    pass  # Ignore cleanup errors
            
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """Main verification function."""
    print("🔍 Trading Backtest System - Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_packages),
        ("Required Files", check_files),
        ("Database Connection", check_database),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        passed = check_func()
        if not passed:
            all_passed = False
    
    # Always check config (informational)
    check_config()
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All checks passed! System is ready to use.")
        print("\n📚 Next steps:")
        print("1. Configure your .env file with FMP API key")
        print("2. Run database setup: python scripts/setup_db.py")
        print("3. Try an example: python scripts/examples/market_cap_strategy.py")
        
        return True
    else:
        print("❌ Some checks failed. Please address the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
