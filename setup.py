"""
Setup script for CryptoMine Pro Mining Pool
This script sets up the mining pool application with all dependencies
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required Python packages"""
    print("Installing Python dependencies...")
    
    requirements = [
        "Flask==2.3.3",
        "Flask-SQLAlchemy==3.0.5", 
        "Flask-Bcrypt==1.0.1",
        "Flask-Login==0.6.3",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "Werkzeug==2.3.7"
    ]
    
    for requirement in requirements:
        try:
            print(f"Installing {requirement}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
            print(f"✓ {requirement} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error installing {requirement}: {e}")
            return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "templates",
        "static/css",
        "static/js", 
        "static/images",
        "instance"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def setup_environment():
    """Setup environment variables"""
    env_content = """# CryptoMine Pro Environment Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///mining_pool.db
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✓ Created .env file")

def main():
    """Main setup function"""
    print("🚀 Setting up CryptoMine Pro Mining Pool...")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        return False
    
    # Create directories
    create_directories()
    
    # Setup environment
    setup_environment()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\nTo start the mining pool:")
    print("1. Run: python app.py")
    print("2. Open your browser to: http://localhost:5000")
    print("\nEnjoy your professional mining pool! 💎")
    
    return True

if __name__ == "__main__":
    main()