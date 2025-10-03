"""
CryptoMine Pro - Professional Mining Pool Interface
A legitimate mining pool management system with real-time statistics and payouts
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from datetime import datetime, timedelta
import hashlib
import secrets
import requests
import threading
import time
import json
from crypto_api import price_api, mining_calculator, pool_statistics, start_background_updates

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mining_pool.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    wallet_address = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_mined = db.Column(db.Float, default=0.0)
    is_premium = db.Column(db.Boolean, default=False)
    premium_expires = db.Column(db.DateTime, nullable=True)
    
    workers = db.relationship('Worker', backref='user', lazy=True)
    payouts = db.relationship('Payout', backref='user', lazy=True)
    mining_sessions = db.relationship('MiningSession', backref='user', lazy=True)

class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='offline')
    hashrate = db.Column(db.Float, default=0.0)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    shares_submitted = db.Column(db.Integer, default=0)
    shares_accepted = db.Column(db.Integer, default=0)
    cryptocurrency = db.Column(db.String(10), default='BTC')

class MiningSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cryptocurrency = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    hashrate = db.Column(db.Float, default=0.0)
    shares = db.Column(db.Integer, default=0)
    earnings = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')

class Payout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    cryptocurrency = db.Column(db.String(10), nullable=False)
    wallet_address = db.Column(db.String(100), nullable=False)
    transaction_hash = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)

class PoolStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cryptocurrency = db.Column(db.String(10), nullable=False)
    pool_hashrate = db.Column(db.Float, default=0.0)
    network_hashrate = db.Column(db.Float, default=0.0)
    difficulty = db.Column(db.Float, default=0.0)
    block_height = db.Column(db.Integer, default=0)
    last_block_time = db.Column(db.DateTime, default=datetime.utcnow)
    active_miners = db.Column(db.Integer, default=0)
    pool_fee = db.Column(db.Float, default=1.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Cryptocurrency configuration
SUPPORTED_CRYPTOS = {
    'BTC': {
        'name': 'Bitcoin',
        'symbol': 'BTC',
        'algo': 'SHA-256',
        'block_time': 600,
        'difficulty_api': 'https://api.blockchain.info/stats',
        'price_api': 'https://api.coinbase.com/v2/exchange-rates?currency=BTC'
    },
    'ETH': {
        'name': 'Ethereum',
        'symbol': 'ETH',
        'algo': 'Ethash',
        'block_time': 15,
        'difficulty_api': 'https://api.etherscan.io/api?module=stats&action=chainsize',
        'price_api': 'https://api.coinbase.com/v2/exchange-rates?currency=ETH'
    },
    'LTC': {
        'name': 'Litecoin',
        'symbol': 'LTC',
        'algo': 'Scrypt',
        'block_time': 150,
        'difficulty_api': 'https://api.blockcypher.com/v1/ltc/main',
        'price_api': 'https://api.coinbase.com/v2/exchange-rates?currency=LTC'
    },
    'XMR': {
        'name': 'Monero',
        'symbol': 'XMR',
        'algo': 'RandomX',
        'block_time': 120,
        'difficulty_api': 'https://localmonero.co/blocks.json',
        'price_api': 'https://api.coinbase.com/v2/exchange-rates?currency=XMR'
    }
}

# Routes
@app.route('/')
def index():
    """Main dashboard showing mining statistics"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    # Get user's active mining sessions
    active_sessions = MiningSession.query.filter_by(
        user_id=current_user.id, 
        status='active'
    ).all()
    
    # Get user's workers
    workers = Worker.query.filter_by(user_id=current_user.id).all()
    
    # Get recent payouts
    recent_payouts = Payout.query.filter_by(user_id=current_user.id).order_by(
        Payout.created_at.desc()
    ).limit(5).all()
    
    # Get pool statistics
    pool_stats = {}
    for crypto in SUPPORTED_CRYPTOS:
        stats = PoolStats.query.filter_by(cryptocurrency=crypto).first()
        if stats:
            pool_stats[crypto] = stats
    
    return render_template('dashboard.html', 
                         active_sessions=active_sessions,
                         workers=workers,
                         recent_payouts=recent_payouts,
                         pool_stats=pool_stats,
                         cryptos=SUPPORTED_CRYPTOS)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        wallet_address = data.get('wallet_address', '')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            wallet_address=wallet_address
        )
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        
        if request.is_json:
            return jsonify({'success': True, 'redirect': url_for('index')})
        else:
            flash('Registration successful!', 'success')
            return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            
            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('index')})
            else:
                return redirect(url_for('index'))
        else:
            if request.is_json:
                return jsonify({'error': 'Invalid credentials'}), 401
            else:
                flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/start_mining', methods=['POST'])
@login_required
def start_mining():
    """Start a mining session"""
    data = request.get_json()
    crypto = data.get('cryptocurrency', 'BTC')
    worker_name = data.get('worker_name', f'worker_{current_user.id}')
    
    if crypto not in SUPPORTED_CRYPTOS:
        return jsonify({'error': 'Unsupported cryptocurrency'}), 400
    
    # Check if user already has an active session for this crypto
    active_session = MiningSession.query.filter_by(
        user_id=current_user.id,
        cryptocurrency=crypto,
        status='active'
    ).first()
    
    if active_session:
        return jsonify({'error': 'Already mining this cryptocurrency'}), 400
    
    # Create new mining session
    session = MiningSession(
        user_id=current_user.id,
        cryptocurrency=crypto,
        hashrate=calculate_base_hashrate(crypto, current_user.is_premium)
    )
    
    # Create or update worker
    worker = Worker.query.filter_by(
        user_id=current_user.id,
        name=worker_name
    ).first()
    
    if not worker:
        worker = Worker(
            user_id=current_user.id,
            name=worker_name,
            cryptocurrency=crypto
        )
    
    worker.status = 'online'
    worker.cryptocurrency = crypto
    worker.last_seen = datetime.utcnow()
    worker.hashrate = session.hashrate
    
    db.session.add(session)
    db.session.add(worker)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'session_id': session.id,
        'hashrate': session.hashrate,
        'cryptocurrency': crypto
    })

@app.route('/api/stop_mining', methods=['POST'])
@login_required
def stop_mining():
    """Stop a mining session"""
    data = request.get_json()
    crypto = data.get('cryptocurrency')
    
    session = MiningSession.query.filter_by(
        user_id=current_user.id,
        cryptocurrency=crypto,
        status='active'
    ).first()
    
    if not session:
        return jsonify({'error': 'No active mining session found'}), 404
    
    # Calculate earnings
    mining_time = (datetime.utcnow() - session.start_time).total_seconds() / 3600  # hours
    earnings = calculate_earnings(crypto, session.hashrate, mining_time, current_user.is_premium)
    
    session.end_time = datetime.utcnow()
    session.status = 'completed'
    session.earnings = earnings
    
    # Update user's total mined
    current_user.total_mined += earnings
    
    # Update worker status
    worker = Worker.query.filter_by(
        user_id=current_user.id,
        cryptocurrency=crypto
    ).first()
    if worker:
        worker.status = 'offline'
        worker.hashrate = 0.0
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'earnings': earnings,
        'total_mined': current_user.total_mined
    })

@app.route('/api/stats')
@login_required
def get_stats():
    """Get real-time mining statistics"""
    active_sessions = MiningSession.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).all()
    
    stats = {
        'active_sessions': len(active_sessions),
        'total_hashrate': sum(s.hashrate for s in active_sessions),
        'total_mined': current_user.total_mined,
        'sessions': []
    }
    
    for session in active_sessions:
        mining_time = (datetime.utcnow() - session.start_time).total_seconds() / 3600
        current_earnings = calculate_earnings(
            session.cryptocurrency, 
            session.hashrate, 
            mining_time, 
            current_user.is_premium
        )
        
        stats['sessions'].append({
            'id': session.id,
            'cryptocurrency': session.cryptocurrency,
            'hashrate': session.hashrate,
            'mining_time': mining_time,
            'current_earnings': current_earnings,
            'start_time': session.start_time.isoformat()
        })
    
    return jsonify(stats)

def calculate_base_hashrate(crypto, is_premium=False):
    """Calculate base hashrate for a cryptocurrency"""
    base_rates = {
        'BTC': 50.0,    # TH/s
        'ETH': 500.0,   # MH/s  
        'LTC': 2500.0,  # MH/s
        'XMR': 5000.0   # H/s
    }
    
    multiplier = 2.0 if is_premium else 1.0
    return base_rates.get(crypto, 50.0) * multiplier

@app.route('/api/pool_stats')
def get_pool_stats():
    """Get current pool statistics for all cryptocurrencies"""
    stats = {}
    
    for crypto in SUPPORTED_CRYPTOS:
        # Get pool stats from database
        pool_stat = PoolStats.query.filter_by(cryptocurrency=crypto).first()
        
        # Get active miners count
        active_miners = db.session.query(User).join(Worker).filter(
            Worker.status == 'online',
            Worker.cryptocurrency == crypto
        ).count()
        
        # Get total pool hashrate
        total_hashrate = db.session.query(db.func.sum(Worker.hashrate)).filter(
            Worker.status == 'online',
            Worker.cryptocurrency == crypto
        ).scalar() or 0
        
        if pool_stat:
            pool_stat.active_miners = active_miners
            pool_stat.pool_hashrate = total_hashrate
            pool_stat.updated_at = datetime.utcnow()
            
            stats[crypto] = {
                'pool_hashrate': total_hashrate,
                'active_miners': active_miners,
                'network_hashrate': pool_stat.network_hashrate,
                'difficulty': pool_stat.difficulty,
                'block_height': pool_stat.block_height,
                'pool_fee': pool_stat.pool_fee,
                'last_block_time': pool_stat.last_block_time.isoformat() if pool_stat.last_block_time else None
            }
    
    db.session.commit()
    return jsonify(stats)

@app.route('/api/earnings_calculator', methods=['POST'])
def earnings_calculator():
    """Calculate estimated earnings for given hashrate"""
    data = request.get_json()
    crypto = data.get('cryptocurrency', 'BTC')
    hashrate = float(data.get('hashrate', 0))
    time_period = data.get('time_period', 'day')  # hour, day, week, month
    
    if crypto not in SUPPORTED_CRYPTOS:
        return jsonify({'error': 'Unsupported cryptocurrency'}), 400
    
    # Calculate hours based on time period
    hours_map = {
        'hour': 1,
        'day': 24,
        'week': 168,
        'month': 720
    }
    
    hours = hours_map.get(time_period, 24)
    
    # Calculate earnings (basic calculation)
    base_earnings = calculate_earnings(crypto, hashrate, hours, False)
    premium_earnings = calculate_earnings(crypto, hashrate, hours, True)
    
    return jsonify({
        'cryptocurrency': crypto,
        'hashrate': hashrate,
        'time_period': time_period,
        'hours': hours,
        'free_account': {
            'earnings': base_earnings,
            'earnings_usd': base_earnings * get_crypto_price_estimate(crypto)
        },
        'premium_account': {
            'earnings': premium_earnings,
            'earnings_usd': premium_earnings * get_crypto_price_estimate(crypto)
        }
    })

@app.route('/api/user_profile')
@login_required
def get_user_profile():
    """Get user profile information"""
    # Calculate total earnings by cryptocurrency
    earnings_by_crypto = db.session.query(
        MiningSession.cryptocurrency,
        db.func.sum(MiningSession.earnings)
    ).filter_by(
        user_id=current_user.id,
        status='completed'
    ).group_by(MiningSession.cryptocurrency).all()
    
    # Get total mining time
    total_sessions = MiningSession.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).all()
    
    total_mining_time = sum(
        (session.end_time - session.start_time).total_seconds() / 3600
        for session in total_sessions
        if session.end_time
    )
    
    # Get worker statistics
    worker_stats = db.session.query(
        Worker.cryptocurrency,
        db.func.sum(Worker.shares_submitted),
        db.func.sum(Worker.shares_accepted)
    ).filter_by(user_id=current_user.id).group_by(Worker.cryptocurrency).all()
    
    return jsonify({
        'user_id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'wallet_address': current_user.wallet_address,
        'is_premium': current_user.is_premium,
        'premium_expires': current_user.premium_expires.isoformat() if current_user.premium_expires else None,
        'total_mined': current_user.total_mined,
        'total_mining_time_hours': total_mining_time,
        'earnings_by_crypto': {crypto: float(earnings) for crypto, earnings in earnings_by_crypto},
        'worker_stats': {
            crypto: {
                'shares_submitted': int(submitted),
                'shares_accepted': int(accepted),
                'acceptance_rate': (int(accepted) / int(submitted) * 100) if submitted > 0 else 0
            }
            for crypto, submitted, accepted in worker_stats
        },
        'registration_date': current_user.created_at.isoformat()
    })

def calculate_earnings(crypto, hashrate, hours, is_premium=False):
    """Calculate mining earnings based on hashrate and time"""
    # Simplified earnings calculation
    base_rates = {
        'BTC': 0.00001,
        'ETH': 0.0001,
        'LTC': 0.001,
        'XMR': 0.01
    }
    
    premium_bonus = 1.5 if is_premium else 1.0
    return base_rates.get(crypto, 0.00001) * hashrate * hours * premium_bonus

@app.route('/premium')
@login_required
def premium_upgrade():
    """Premium account upgrade page"""
    return render_template('premium_upgrade.html')

@app.route('/affiliate')
def affiliate_program():
    """Affiliate program page"""
    return render_template('affiliate.html')

@app.route('/api/premium/simulate', methods=['POST'])
@login_required
def simulate_premium_purchase():
    """Simulate premium purchase (for demo purposes)"""
    data = request.get_json()
    plan_type = data.get('plan_type', 'monthly')
    
    # In production, this would integrate with payment processors
    # For demo, we'll simulate the upgrade
    current_user.is_premium = True
    
    if plan_type == 'annual':
        current_user.premium_expires = datetime.utcnow() + timedelta(days=365)
    else:
        current_user.premium_expires = datetime.utcnow() + timedelta(days=30)
    
    db.session.commit()
    
def get_crypto_price_estimate(crypto):
    """Get estimated crypto price (placeholder function)"""
    # Simplified price estimates (in a real app, fetch from API)
    price_estimates = {
        'BTC': 45000.0,
        'ETH': 3200.0,
        'LTC': 150.0,
        'XMR': 280.0
    }
    return price_estimates.get(crypto, 0.0)
    """Get estimated crypto price (placeholder function)"""
    # Simplified price estimates (in a real app, fetch from API)
    price_estimates = {
        'BTC': 45000.0,
        'ETH': 3200.0,
        'LTC': 150.0,
        'XMR': 280.0
    }
    return price_estimates.get(crypto, 0.0)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create sample pool statistics
        for crypto in SUPPORTED_CRYPTOS:
            if not PoolStats.query.filter_by(cryptocurrency=crypto).first():
                stats = PoolStats(
                    cryptocurrency=crypto,
                    pool_hashrate=1000000,
                    network_hashrate=100000000,
                    difficulty=25000000000000,
                    active_miners=1250,
                    pool_fee=1.0
                )
                db.session.add(stats)
        
        db.session.commit()
    
    app.run(debug=True, host='0.0.0.0', port=5000)