#!/bin/bash

# Create the repository
mkdir -p trading-backtest
cd trading-backtest

# Initialize git repository
git init

# Create directory structure
mkdir -p config data/connectors strategies backtest reporting/templates scripts/examples tests

# Create all Python __init__.py files
touch config/__init__.py
touch data/__init__.py
touch data/connectors/__init__.py
touch strategies/__init__.py
touch backtest/__init__.py
touch reporting/__init__.py
touch tests/__init__.py

# Create .gitignore
cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
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

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Project specific
config/settings.py
reports/*.pdf
reports/*.html
*.log
.DS_Store

# Database
*.db
*.sqlite3
trading_data/
EOF

# Create .env.example
cat > .env.example << 'EOF'
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_backtest
DB_USER=trader
DB_PASSWORD=trader_password

# API Keys
FMP_API_KEY=your_api_key_here
EOF

# Create the README
cat > README.md << 'EOF'
# Trading Strategy Backtest System

A Python-based backtesting framework for testing trading strategies with screening, allocation, and signal generation capabilities.

## Features
- Stock screening (market cap, fundamentals, custom indicators)
- Portfolio allocation strategies
- Buy/sell signal generation
- Performance analytics and PDF reporting
- Data caching with PostgreSQL/TimescaleDB
- Integration with Financial Modeling Prep API

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Zruvan/trading-backtest.git
cd trading-backtest