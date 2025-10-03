#!/bin/bash
# Heroku Deployment Script for CryptoMine Pro
# Run this script to deploy your mining pool to Heroku

echo "🚀 CryptoMine Pro - Heroku Deployment Script"
echo "=============================================="

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found!"
    echo "📥 Please install from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if git is configured
if ! git config user.name &> /dev/null; then
    echo "⚙️ Configuring Git..."
    git config --global user.name "CryptoMiner"
    git config --global user.email "miner@cryptominepro.com"
fi

# Initialize git repository if not exists
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - CryptoMine Pro Mining Pool"
fi

# Get app name from user
read -p "🏷️ Enter your Heroku app name (e.g., my-crypto-mining-pool): " APP_NAME

# Create Heroku app
echo "🆕 Creating Heroku app: $APP_NAME..."
heroku create $APP_NAME

# Add PostgreSQL addon
echo "🗄️ Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:mini

# Set environment variables
echo "⚙️ Setting environment variables..."
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$SECRET_KEY

# Deploy to Heroku
echo "🚀 Deploying to Heroku..."
git push heroku main

# Initialize database
echo "🗄️ Initializing database..."
heroku run python -c "from app import db; db.create_all()"

# Get the app URL
APP_URL="https://$APP_NAME.herokuapp.com"

echo "✅ Deployment completed successfully!"
echo "🌐 Your mining pool is live at: $APP_URL"
echo "💰 Start earning money now!"

# Open in browser
read -p "🌐 Open your app in browser? (y/n): " OPEN_BROWSER
if [ "$OPEN_BROWSER" = "y" ]; then
    heroku open
fi