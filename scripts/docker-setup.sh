#!/bin/bash
# Docker development setup script

set -e

echo "🐳 Setting up Trading Backtest System with Docker"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env.docker exists
if [ ! -f .env.docker ]; then
    echo "📝 Creating Docker environment file..."
    cp .env.docker .env.docker.local
    echo "⚠️  Please edit .env.docker.local with your API keys and settings"
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d database

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "🏗️  Setting up database..."
docker-compose run --rm app python scripts/setup_db.py

echo "✅ Setup complete!"
echo ""
echo "📊 Available services:"
echo "  - Database: localhost:5432"
echo "  - Application: docker-compose run --rm app python <script>"
echo ""
echo "🔧 Useful commands:"
echo "  - Start all services: docker-compose up -d"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Run tests: docker-compose run --rm app python -m pytest"
echo "  - Start Jupyter: docker-compose --profile jupyter up -d jupyter"
echo "  - Access database: docker-compose exec database psql -U postgres -d trading_backtest"
echo ""
echo "🎉 Ready to start backtesting!"
