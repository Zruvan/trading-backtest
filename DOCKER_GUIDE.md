# Docker Setup Guide

This guide explains how to use Docker with the Trading Backtest System for development and production environments.

## 🐳 Quick Start

### Prerequisites
- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- Docker Compose v2+

### Windows Setup
```batch
# Run the setup script
scripts\docker-setup.bat

# Or manually:
docker-compose up -d database
docker-compose run --rm app python scripts/setup_db.py
```

### Linux/macOS Setup
```bash
# Make script executable and run
chmod +x scripts/docker-setup.sh
./scripts/docker-setup.sh

# Or manually:
docker-compose up -d database
docker-compose run --rm app python scripts/setup_db.py
```

## 📋 Available Services

### Core Services
- **database**: TimescaleDB (PostgreSQL 15) with time-series extensions
- **app**: Main application container

### Optional Services (Use Profiles)
- **jupyter**: Jupyter notebook server for analysis
- **redis**: Redis cache for improved performance

## 🚀 Usage Examples

### Basic Operations
```bash
# Start database only
docker-compose up -d database

# Run verification
docker-compose run --rm app python verify_setup.py

# Run tests
docker-compose run --rm app python -m pytest -v

# Run a backtest example
docker-compose run --rm app python scripts/examples/buy_sell_threshold_strategy.py

# View logs
docker-compose logs -f app
docker-compose logs -f database
```

### Development with Jupyter
```bash
# Start with Jupyter notebook
docker-compose --profile jupyter up -d

# Access Jupyter at http://localhost:8888
# No password required (development setup)
```

### Production with Caching
```bash
# Start with Redis caching
docker-compose --profile cache up -d

# Start all services including optional ones
docker-compose --profile jupyter --profile cache up -d
```

### Database Operations
```bash
# Access database directly
docker-compose exec database psql -U postgres -d trading_backtest

# Reset database
docker-compose down -v  # Remove volumes
docker-compose up -d database
docker-compose run --rm app python scripts/setup_db.py
```

## ⚙️ Configuration

### Environment Files
- `.env.docker`: Template for Docker environment variables
- `.env.docker.local`: Local overrides (git-ignored)

### Key Environment Variables
```bash
# Database
DB_HOST=database
DB_PORT=5432
DB_NAME=trading_backtest
DB_USER=postgres
DB_PASSWORD=password

# API Keys
FMP_API_KEY=your_api_key_here

# Application
DEBUG=false
LOG_LEVEL=INFO
USE_SQLITE=false
```

### Volume Mounts
- `./reports:/app/reports` - Generated reports
- `./data:/app/data` - Data cache and files
- `postgres_data:/var/lib/postgresql/data` - Database persistence
- `app_logs:/app/logs` - Application logs

## 🔧 Development Workflow

### 1. Initial Setup
```bash
# Clone and setup
git clone <repository>
cd trading-backtest
cp .env.docker .env.docker.local
# Edit .env.docker.local with your settings
scripts/docker-setup.sh  # or .bat on Windows
```

### 2. Daily Development
```bash
# Start services
docker-compose up -d

# Develop and test
docker-compose run --rm app python your_script.py

# View logs
docker-compose logs -f app

# Stop when done
docker-compose down
```

### 3. Code Changes
```bash
# Rebuild after code changes
docker-compose build app

# Or rebuild and restart
docker-compose up -d --build app
```

## 🏗️ Production Deployment

### 1. Environment Setup
```bash
# Production environment file
cp .env.docker .env.production
# Edit with production settings:
# - Strong passwords
# - Production API keys
# - Disable debug mode
# - Set appropriate log levels
```

### 2. Deployment
```bash
# Deploy with production config
docker-compose --env-file .env.production up -d

# Health checks
docker-compose ps
docker-compose logs app
docker-compose exec app python verify_setup.py
```

### 3. Maintenance
```bash
# Backup database
docker-compose exec database pg_dump -U postgres trading_backtest > backup.sql

# Update application
git pull
docker-compose build app
docker-compose up -d --no-deps app

# Monitor
docker-compose logs -f --tail=100 app
```

## 🐛 Troubleshooting

### Common Issues

**Database connection failed**
```bash
# Check database is ready
docker-compose ps database
docker-compose logs database

# Restart database
docker-compose restart database
```

**Port already in use**
```bash
# Check what's using the port
netstat -an | findstr :5432  # Windows
lsof -i :5432                # Linux/macOS

# Use different ports in docker-compose.yml
ports:
  - "5433:5432"  # Use 5433 instead
```

**Build failures**
```bash
# Clean build
docker-compose down
docker system prune -f
docker-compose build --no-cache app
```

**Permission errors (Linux/macOS)**
```bash
# Fix volume permissions
sudo chown -R $USER:$USER ./reports ./data
```

### Performance Tuning

**Database Performance**
```bash
# Increase shared_buffers in docker-compose.yml
services:
  database:
    command: >
      postgres
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c work_mem=4MB
```

**Application Performance**
```bash
# Use Redis caching
docker-compose --profile cache up -d

# Monitor resource usage
docker stats
```

## 📊 Monitoring

### Health Checks
```bash
# Application health
docker-compose run --rm app python verify_setup.py

# Database health
docker-compose exec database pg_isready -U postgres

# Service status
docker-compose ps
```

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f database

# With timestamps
docker-compose logs -f -t app
```

### Resource Usage
```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up unused resources
docker system prune -f
```

## 🔒 Security Notes

### Development
- Default passwords are used for convenience
- No SSL/TLS encryption
- Jupyter has no authentication
- Database ports are exposed

### Production
- Change all default passwords
- Use environment variables for secrets
- Enable SSL/TLS
- Restrict network access
- Use Docker secrets for sensitive data
- Regular security updates

### Example Production Security
```yaml
# docker-compose.prod.yml
services:
  database:
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    ports: []  # Don't expose to host

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

This Docker setup provides a complete, scalable environment for both development and production use of the Trading Backtest System.
