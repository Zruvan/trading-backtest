#!/bin/bash

# Initialize git repository
git init

# Create initial commit
git add .
git commit -m "Initial commit: Trading backtest system framework"

# Create main branch
git branch -M main

# Add remote (you'll need to create the repo on GitHub first)
# git remote add origin https://github.com/Zruvan/trading-backtest.git
# git push -u origin main

echo "Repository initialized!"
echo ""
echo "Next steps:"
echo "1. Create a repository on GitHub named 'trading-backtest'"
echo "2. Run: git remote add origin https://github.com/Zruvan/trading-backtest.git"
echo "3. Run: git push -u origin main"