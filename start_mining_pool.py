"""
CryptoMine Pro - Mining Pool Startup Script
This script starts the mining pool application with proper initialization
"""

import os
import sys
import subprocess
import time
import webbrowser
from threading import Timer

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = [
        'flask',
        'flask_sqlalchemy', 
        'flask_bcrypt',
        'flask_login',
        'requests'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    return missing_modules

def install_dependencies():
    """Install missing dependencies"""
    print("Installing missing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def open_browser():
    """Open the mining pool in the default browser"""
    url = "http://localhost:5000"
    print(f"🌐 Opening mining pool in browser: {url}")
    webbrowser.open(url)

def main():
    """Main startup function"""
    print("🚀 Starting CryptoMine Pro Mining Pool...")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found!")
        print("Please make sure you're in the mining_pool directory")
        return
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"⚠️  Missing dependencies: {', '.join(missing)}")
        if not install_dependencies():
            print("❌ Failed to install dependencies. Please run setup.py first.")
            return
    
    print("✅ All dependencies are ready!")
    print("\n🔧 Initializing mining pool...")
    
    # Schedule browser opening after 3 seconds
    Timer(3.0, open_browser).start()
    
    print("🎯 Mining pool will be available at: http://localhost:5000")
    print("📊 Dashboard will open automatically in your browser")
    print("\n💡 Press Ctrl+C to stop the mining pool")
    print("=" * 60)
    
    try:
        # Start the Flask application
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n\n🛑 Mining pool stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting mining pool: {e}")

if __name__ == "__main__":
    main()