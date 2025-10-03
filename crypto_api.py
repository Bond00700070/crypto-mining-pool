"""
Cryptocurrency API integration for real-time prices and network statistics
"""

import requests
import json
import time
from datetime import datetime, timedelta
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoPriceAPI:
    """Handle cryptocurrency price and network data fetching"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        self.last_update = {}
        
    def get_crypto_prices(self, symbols=['BTC', 'ETH', 'LTC', 'XMR']):
        """Get current cryptocurrency prices"""
        try:
            # Use CoinGecko API for reliable price data
            ids = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum', 
                'LTC': 'litecoin',
                'XMR': 'monero'
            }
            
            coin_ids = ','.join([ids.get(symbol) or symbol.lower() for symbol in symbols])
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert back to symbol format
            prices = {}
            reverse_ids = {v: k for k, v in ids.items()}
            
            for coin_id, price_data in data.items():
                symbol = reverse_ids.get(coin_id, coin_id.upper())
                prices[symbol] = {
                    'price': price_data.get('usd', 0),
                    'change_24h': price_data.get('usd_24h_change', 0),
                    'volume_24h': price_data.get('usd_24h_vol', 0)
                }
            
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching crypto prices: {e}")
            return {}
    
    def get_bitcoin_network_stats(self):
        """Get Bitcoin network statistics"""
        try:
            # Multiple APIs for redundancy
            apis = [
                "https://api.blockchain.info/stats",
                "https://blockchair.com/bitcoin/stats"
            ]
            
            for api_url in apis:
                try:
                    response = requests.get(api_url, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    if 'difficulty' in data:
                        return {
                            'difficulty': data.get('difficulty', 0),
                            'network_hashrate': data.get('hash_rate', 0) * 1000000000,  # Convert to H/s
                            'block_height': data.get('n_blocks_total', 0),
                            'mempool_size': data.get('n_tx_mempool', 0)
                        }
                except:
                    continue
                    
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching Bitcoin network stats: {e}")
            return {}
    
    def get_ethereum_network_stats(self):
        """Get Ethereum network statistics"""
        try:
            # Use Etherscan API
            api_key = "YourEtherscanAPIKey"  # Replace with actual API key
            base_url = "https://api.etherscan.io/api"
            
            # Get latest block
            params = {
                'module': 'proxy',
                'action': 'eth_blockNumber',
                'apikey': api_key
            }
            
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            block_data = response.json()
            block_height = int(block_data.get('result', '0x0'), 16)
            
            return {
                'block_height': block_height,
                'difficulty': 0,  # ETH 2.0 doesn't use PoW difficulty
                'network_hashrate': 0
            }
            
        except Exception as e:
            logger.error(f"Error fetching Ethereum network stats: {e}")
            return {}
    
    def get_cached_data(self, key):
        """Get cached data if still valid"""
        if key in self.cache and key in self.last_update:
            if datetime.now() - self.last_update[key] < timedelta(seconds=self.cache_duration):
                return self.cache[key]
        return None
    
    def set_cached_data(self, key, data):
        """Set cached data with timestamp"""
        self.cache[key] = data
        self.last_update[key] = datetime.now()

class MiningCalculator:
    """Calculate mining profitability and earnings"""
    
    def __init__(self, price_api):
        self.price_api = price_api
    
    def calculate_mining_reward(self, crypto, hashrate, hours, is_premium=False):
        """Calculate mining reward based on hashrate and time"""
        
        # Get current crypto price
        prices = self.price_api.get_crypto_prices([crypto])
        crypto_price = prices.get(crypto, {}).get('price', 0)
        
        # Base mining rates (coins per TH/s per hour)
        base_rates = {
            'BTC': 0.00000156,  # Realistic BTC mining rate
            'ETH': 0.000012,    # ETH mining rate (pre-merge for simulation)
            'LTC': 0.000098,    # Litecoin mining rate
            'XMR': 0.0008       # Monero mining rate
        }
        
        # Difficulty adjustment factor (simulates network difficulty)
        difficulty_factors = {
            'BTC': 1.0,
            'ETH': 0.8,
            'LTC': 1.2,
            'XMR': 1.5
        }
        
        base_rate = base_rates.get(crypto, 0.00000156)
        difficulty_factor = difficulty_factors.get(crypto, 1.0)
        premium_multiplier = 2.0 if is_premium else 1.0
        
        # Calculate coins earned
        coins_earned = base_rate * hashrate * hours * difficulty_factor * premium_multiplier
        
        # Add some randomness to simulate real mining variance
        import random
        variance = random.uniform(0.85, 1.15)
        coins_earned *= variance
        
        return {
            'coins': coins_earned,
            'usd_value': coins_earned * crypto_price if crypto_price else 0,
            'crypto_price': crypto_price
        }
    
    def get_mining_profitability(self, crypto, hashrate, power_consumption=0, electricity_cost=0.1):
        """Calculate mining profitability"""
        
        # Calculate daily rewards
        daily_reward = self.calculate_mining_reward(crypto, hashrate, 24)
        
        # Calculate daily electricity cost
        daily_power_cost = (power_consumption / 1000) * 24 * electricity_cost
        
        # Calculate profit
        daily_profit = daily_reward['usd_value'] - daily_power_cost
        
        return {
            'daily_revenue': daily_reward['usd_value'],
            'daily_costs': daily_power_cost,
            'daily_profit': daily_profit,
            'daily_coins': daily_reward['coins'],
            'roi_days': (1000 / daily_profit) if daily_profit > 0 else float('inf')  # Assuming $1000 mining rig
        }

class PoolStatistics:
    """Manage mining pool statistics"""
    
    def __init__(self, price_api):
        self.price_api = price_api
        self.stats = {}
    
    def update_pool_stats(self, crypto, active_miners, total_hashrate):
        """Update pool statistics for a cryptocurrency"""
        
        # Get network stats
        if crypto == 'BTC':
            network_stats = self.price_api.get_bitcoin_network_stats()
        elif crypto == 'ETH':
            network_stats = self.price_api.get_ethereum_network_stats()
        else:
            network_stats = {}
        
        # Calculate pool percentage of network
        network_hashrate = network_stats.get('network_hashrate', 100000000000)  # Default 100 GH/s
        pool_percentage = (total_hashrate / network_hashrate) * 100 if network_hashrate > 0 else 0
        
        # Estimate blocks found per day
        if crypto == 'BTC':
            blocks_per_day = 144  # Bitcoin: ~10 minutes per block
        elif crypto == 'ETH':
            blocks_per_day = 5760  # Ethereum: ~15 seconds per block
        elif crypto == 'LTC':
            blocks_per_day = 576   # Litecoin: ~2.5 minutes per block
        else:
            blocks_per_day = 720   # Default: ~2 minutes per block
        
        estimated_blocks_per_day = blocks_per_day * (pool_percentage / 100)
        
        self.stats[crypto] = {
            'active_miners': active_miners,
            'pool_hashrate': total_hashrate,
            'network_hashrate': network_hashrate,
            'pool_percentage': pool_percentage,
            'difficulty': network_stats.get('difficulty', 0),
            'block_height': network_stats.get('block_height', 0),
            'estimated_blocks_per_day': estimated_blocks_per_day,
            'last_updated': datetime.now()
        }
        
        return self.stats[crypto]
    
    def get_pool_stats(self, crypto):
        """Get pool statistics for a cryptocurrency"""
        return self.stats.get(crypto, {})

# Initialize global instances
price_api = CryptoPriceAPI()
mining_calculator = MiningCalculator(price_api)
pool_statistics = PoolStatistics(price_api)

def start_background_updates():
    """Start background thread to update cryptocurrency data"""
    
    def update_crypto_data():
        while True:
            try:
                # Update prices every 5 minutes
                logger.info("Updating cryptocurrency prices...")
                prices = price_api.get_crypto_prices()
                logger.info(f"Updated prices for {len(prices)} cryptocurrencies")
                
                # Update network stats every 10 minutes
                logger.info("Updating network statistics...")
                btc_stats = price_api.get_bitcoin_network_stats()
                eth_stats = price_api.get_ethereum_network_stats()
                
                time.sleep(300)  # Sleep for 5 minutes
                
            except Exception as e:
                logger.error(f"Error in background update: {e}")
                time.sleep(60)  # Sleep for 1 minute on error
    
    # Start background thread
    update_thread = threading.Thread(target=update_crypto_data, daemon=True)
    update_thread.start()
    logger.info("Started background cryptocurrency data updates")

if __name__ == "__main__":
    # Test the API
    print("Testing CryptoPriceAPI...")
    
    prices = price_api.get_crypto_prices()
    print(f"Current prices: {prices}")
    
    btc_stats = price_api.get_bitcoin_network_stats()
    print(f"Bitcoin network stats: {btc_stats}")
    
    # Test mining calculator
    btc_reward = mining_calculator.calculate_mining_reward('BTC', 50, 1)  # 50 TH/s for 1 hour
    print(f"BTC mining reward for 50 TH/s, 1 hour: {btc_reward}")
    
    profitability = mining_calculator.get_mining_profitability('BTC', 50, 3000, 0.1)
    print(f"BTC mining profitability: {profitability}")