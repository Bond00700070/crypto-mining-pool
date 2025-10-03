"""
Quick Deployment Script for CryptoMine Pro
This script helps you deploy your mining pool to various platforms
"""

import os
import subprocess
import sys
import webbrowser
import time

def print_header(title):
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_success(message):
    print(f"✅ {message}")

def print_info(message):
    print(f"💡 {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def check_git():
    """Check if git is installed and initialized"""
    try:
        subprocess.run(['git', '--version'], check=True, capture_output=True)
        return True
    except:
        return False

def initialize_git():
    """Initialize git repository"""
    try:
        if not os.path.exists('.git'):
            subprocess.run(['git', 'init'], check=True)
            print_success("Git repository initialized")
        
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit - CryptoMine Pro'], check=True)
        print_success("Files committed to git")
        return True
    except Exception as e:
        print_warning(f"Git setup failed: {e}")
        return False

def deploy_to_heroku():
    """Deploy to Heroku"""
    print_header("Deploying to Heroku")
    
    app_name = input("Enter your desired app name (e.g., my-crypto-mining-pool): ")
    
    try:
        # Check if Heroku CLI is installed
        subprocess.run(['heroku', '--version'], check=True, capture_output=True)
        
        # Create Heroku app
        print_info("Creating Heroku app...")
        subprocess.run(['heroku', 'create', app_name], check=True)
        
        # Add PostgreSQL addon
        print_info("Adding PostgreSQL database...")
        subprocess.run(['heroku', 'addons:create', 'heroku-postgresql:mini'], check=True)
        
        # Set environment variables
        print_info("Setting environment variables...")
        subprocess.run(['heroku', 'config:set', 'FLASK_ENV=production'], check=True)
        subprocess.run(['heroku', 'config:set', f'SECRET_KEY={os.urandom(24).hex()}'], check=True)
        
        # Deploy
        print_info("Deploying to Heroku...")
        subprocess.run(['git', 'push', 'heroku', 'main'], check=True)
        
        # Initialize database
        print_info("Initializing database...")
        subprocess.run(['heroku', 'run', 'python', '-c', 'from app import db; db.create_all()'], check=True)
        
        # Open the app
        print_success(f"Deployment successful! Your app is live at: https://{app_name}.herokuapp.com")
        
        if input("Open your app in browser? (y/n): ").lower() == 'y':
            webbrowser.open(f"https://{app_name}.herokuapp.com")
            
        return f"https://{app_name}.herokuapp.com"
        
    except subprocess.CalledProcessError:
        print_warning("Heroku CLI not found. Please install it from: https://devcenter.heroku.com/articles/heroku-cli")
        return None
    except Exception as e:
        print_warning(f"Heroku deployment failed: {e}")
        return None

def deploy_to_railway():
    """Deploy to Railway"""
    print_header("Deploying to Railway")
    
    try:
        # Check if Railway CLI is installed
        subprocess.run(['railway', '--version'], check=True, capture_output=True)
        
        # Login and deploy
        print_info("Deploying to Railway...")
        subprocess.run(['railway', 'login'], check=True)
        subprocess.run(['railway', 'init'], check=True)
        subprocess.run(['railway', 'up'], check=True)
        
        print_success("Railway deployment initiated!")
        print_info("Visit https://railway.app/dashboard to manage your deployment")
        
        return "https://railway.app/dashboard"
        
    except subprocess.CalledProcessError:
        print_warning("Railway CLI not found. Please install it from: https://railway.app/cli")
        return None
    except Exception as e:
        print_warning(f"Railway deployment failed: {e}")
        return None

def deploy_to_render():
    """Deploy to Render"""
    print_header("Deploying to Render")
    
    print_info("For Render deployment:")
    print("1. Push your code to GitHub")
    print("2. Go to https://render.com")
    print("3. Create new Web Service")
    print("4. Connect your GitHub repository")
    print("5. Use these settings:")
    print("   - Build Command: pip install -r requirements-prod.txt")
    print("   - Start Command: gunicorn app:app")
    print("   - Environment: Python 3.11")
    
    if input("Open Render in browser? (y/n): ").lower() == 'y':
        webbrowser.open("https://render.com")
    
    return "https://render.com"

def setup_payment_processing():
    """Guide for setting up payment processing"""
    print_header("Payment Processing Setup")
    
    print_info("To start earning money, you need to set up payment processing:")
    print("\n1. Stripe (Recommended for subscriptions):")
    print("   - Sign up at: https://stripe.com")
    print("   - Get API keys from dashboard")
    print("   - Add to environment variables")
    
    print("\n2. PayPal (For affiliate payouts):")
    print("   - Sign up at: https://developer.paypal.com")
    print("   - Create application")
    print("   - Get client ID and secret")
    
    print("\n3. Cryptocurrency payments:")
    print("   - Set up wallet addresses")
    print("   - Use payment processors like BitPay")
    
    if input("Open Stripe signup? (y/n): ").lower() == 'y':
        webbrowser.open("https://stripe.com")

def create_marketing_plan():
    """Create marketing strategy"""
    print_header("Marketing Strategy")
    
    print_info("Here's your marketing action plan:")
    
    print("\n🎯 Immediate Actions (Today):")
    print("1. Share on social media (Twitter, Facebook, Instagram)")
    print("2. Post in Reddit communities (r/cryptomining, r/cryptocurrency)")
    print("3. Create YouTube video showcasing your platform")
    print("4. Join Discord crypto communities")
    
    print("\n📈 Week 1 Actions:")
    print("1. Write blog post about cryptocurrency mining")
    print("2. Reach out to crypto influencers")
    print("3. Set up Google Analytics")
    print("4. Create affiliate recruitment campaign")
    
    print("\n💰 Month 1 Goals:")
    print("1. 100+ registered users")
    print("2. 10+ premium subscriptions")
    print("3. 5+ active affiliates")
    print("4. $500+ monthly revenue")
    
    if input("Create sample social media posts? (y/n): ").lower() == 'y':
        create_social_media_content()

def create_social_media_content():
    """Generate social media content"""
    posts = [
        "🚀 Just launched CryptoMine Pro - a professional mining pool with real-time statistics! Start mining Bitcoin, Ethereum, and more. #cryptocurrency #mining #bitcoin",
        
        "💎 Earning passive income through cryptocurrency mining has never been easier! Check out our new platform with 2x premium speeds. #cryptomining #passiveincome",
        
        "🔥 New affiliate program live! Earn 30% lifetime commissions by referring miners to our platform. Join now! #affiliate #cryptocurrency #earnmoney",
        
        "📊 Real-time mining statistics, multiple cryptocurrencies, and professional-grade features. This is the future of mining pools! #mining #crypto #technology"
    ]
    
    print("\n📱 Sample Social Media Posts:")
    for i, post in enumerate(posts, 1):
        print(f"\n{i}. {post}")
    
    print("\n💡 Pro tip: Customize these posts with your actual website URL!")

def show_revenue_calculator():
    """Show potential revenue"""
    print_header("Revenue Calculator")
    
    try:
        users = int(input("How many users do you expect in Month 1? (default: 100): ") or "100")
        conversion_rate = float(input("Expected premium conversion rate % (default: 10): ") or "10") / 100
        
        premium_users = int(users * conversion_rate)
        monthly_revenue = premium_users * 19  # $19 per premium user
        affiliate_revenue = users * 0.5  # Estimated affiliate revenue
        total_revenue = monthly_revenue + affiliate_revenue
        
        print(f"\n💰 Revenue Projection:")
        print(f"   Total Users: {users}")
        print(f"   Premium Users: {premium_users}")
        print(f"   Premium Revenue: ${monthly_revenue:,.2f}/month")
        print(f"   Affiliate Revenue: ${affiliate_revenue:,.2f}/month")
        print(f"   Total Revenue: ${total_revenue:,.2f}/month")
        print(f"   Annual Revenue: ${total_revenue * 12:,.2f}/year")
        
    except ValueError:
        print_warning("Invalid input. Using default projections:")
        print("   100 users, 10 premium users")
        print("   Monthly Revenue: $190")
        print("   Annual Revenue: $2,280")

def main():
    """Main deployment workflow"""
    print_header("CryptoMine Pro - Quick Deployment & Monetization")
    
    print("Welcome! Let's get your mining pool live and earning money! 💰")
    
    # Check prerequisites
    if not check_git():
        print_warning("Git is required for deployment. Please install Git first.")
        return
    
    # Initialize git if needed
    initialize_git()
    
    # Choose deployment platform
    print("\n🚀 Choose your deployment platform:")
    print("1. Heroku (Recommended - Easy, $7/month)")
    print("2. Railway (Fast, $5/month)")
    print("3. Render (Free tier available)")
    print("4. Manual deployment guide")
    
    choice = input("\nEnter your choice (1-4): ")
    
    deployed_url = None
    
    if choice == "1":
        deployed_url = deploy_to_heroku()
    elif choice == "2":
        deployed_url = deploy_to_railway()
    elif choice == "3":
        deployed_url = deploy_to_render()
    elif choice == "4":
        print_info("Check DEPLOYMENT_GUIDE.md for manual deployment instructions")
    
    # Set up monetization
    if deployed_url:
        print_success(f"Your mining pool is live at: {deployed_url}")
        
        if input("\nSet up payment processing now? (y/n): ").lower() == 'y':
            setup_payment_processing()
        
        if input("\nCreate marketing plan? (y/n): ").lower() == 'y':
            create_marketing_plan()
        
        if input("\nShow revenue projections? (y/n): ").lower() == 'y':
            show_revenue_calculator()
    
    print_header("🎉 Congratulations!")
    print("Your professional mining pool is ready to start earning money!")
    print("\n📋 Next Steps:")
    print("1. Set up payment processing (Stripe, PayPal)")
    print("2. Add your bank account for payouts")
    print("3. Start marketing on social media")
    print("4. Recruit affiliates to grow faster")
    print("\n💎 Your platform can generate $2,000-50,000+ monthly with proper marketing!")

if __name__ == "__main__":
    main()