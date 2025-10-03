@echo off
REM Heroku Deployment Script for Windows - CryptoMine Pro
echo 🚀 CryptoMine Pro - Heroku Deployment Script
echo ==============================================

REM Check if Heroku CLI is installed
heroku --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Heroku CLI not found!
    echo 📥 Please install from: https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

REM Configure Git if not configured
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚙️ Configuring Git...
    git config --global user.name "CryptoMiner"
    git config --global user.email "miner@cryptominepro.com"
)

REM Initialize git repository if not exists
if not exist ".git" (
    echo 📁 Initializing Git repository...
    git init
    git add .
    git commit -m "Initial commit - CryptoMine Pro Mining Pool"
)

REM Get app name from user
set /p APP_NAME="🏷️ Enter your Heroku app name (e.g., my-crypto-mining-pool): "

REM Create Heroku app
echo 🆕 Creating Heroku app: %APP_NAME%...
heroku create %APP_NAME%

REM Add PostgreSQL addon
echo 🗄️ Adding PostgreSQL database...
heroku addons:create heroku-postgresql:mini

REM Set environment variables
echo ⚙️ Setting environment variables...
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" > temp_secret.txt
for /f "tokens=*" %%a in (temp_secret.txt) do heroku config:set %%a
del temp_secret.txt
heroku config:set FLASK_ENV=production

REM Deploy to Heroku
echo 🚀 Deploying to Heroku...
git push heroku main

REM Initialize database
echo 🗄️ Initializing database...
heroku run python -c "from app import db; db.create_all()"

echo ✅ Deployment completed successfully!
echo 🌐 Your mining pool is live at: https://%APP_NAME%.herokuapp.com
echo 💰 Start earning money now!

REM Open in browser
set /p OPEN_BROWSER="🌐 Open your app in browser? (y/n): "
if /i "%OPEN_BROWSER%"=="y" heroku open

pause