#!/usr/bin/env python3
"""
Setup verification script for trading-backtest system.
Run this script to verify that all components are properly installed and configured.
"""

import sys
import os
import traceback
from typing import List, Tuple

def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        return True, f"✓ Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"✗ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)"

def check_imports() -> List[Tuple[bool, str]]:
    """Check if all required modules can be imported"""
    results = []
    
    # Core modules
    modules = [
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('requests', 'requests'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),
        ('reportlab', 'reportlab'),
    ]
    
    for module, display_name in modules:
        try:
            __import__(module)
            results.append((True, f"✓ {display_name}"))
        except ImportError:
            results.append((False, f"✗ {display_name} (not installed)"))
    
    return results

def check_project_structure() -> List[Tuple[bool, str]]:
    """Check if project directories exist"""
    results = []
    
    required_dirs = [
        'backtest',
        'config', 
        'data',
        'strategies',
        'reporting',
        'scripts'
    ]
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            results.append((True, f"✓ {dir_name}/ directory"))
        else:
            results.append((False, f"✗ {dir_name}/ directory missing"))
    
    return results

def check_config_files() -> List[Tuple[bool, str]]:
    """Check configuration files"""
    results = []
    
    # Check if .env exists
    if os.path.exists('.env'):
        results.append((True, "✓ .env file exists"))
    else:
        results.append((False, "✗ .env file missing (copy from .env.example)"))
    
    # Check config files
    config_files = ['config/settings.py', 'config/constants.py']
    for config_file in config_files:
        if os.path.exists(config_file):
            results.append((True, f"✓ {config_file}"))
        else:
            results.append((False, f"✗ {config_file} missing"))
    
    return results

def check_core_modules() -> List[Tuple[bool, str]]:
    """Check if core project modules can be imported"""
    results = []
    
    modules = [
        'backtest.engine',
        'strategies.base',
        'data.database',
        'config.settings'
    ]
    
    for module in modules:
        try:
            __import__(module)
            results.append((True, f"✓ {module}"))
        except Exception as e:
            results.append((False, f"✗ {module} ({str(e)})"))
    
    return results

def main():
    """Run all verification checks"""
    print("Trading Backtest System - Setup Verification")
    print("=" * 50)
    
    all_passed = True
    
    # Check Python version
    passed, message = check_python_version()
    print(f"\nPython Version:")
    print(f"  {message}")
    if not passed:
        all_passed = False
    
    # Check imports
    print(f"\nRequired Packages:")
    for passed, message in check_imports():
        print(f"  {message}")
        if not passed:
            all_passed = False
    
    # Check project structure
    print(f"\nProject Structure:")
    for passed, message in check_project_structure():
        print(f"  {message}")
        if not passed:
            all_passed = False
    
    # Check config files
    print(f"\nConfiguration:")
    for passed, message in check_config_files():
        print(f"  {message}")
        if not passed:
            all_passed = False
    
    # Check core modules
    print(f"\nCore Modules:")
    for passed, message in check_core_modules():
        print(f"  {message}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All checks passed! System is ready to use.")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
