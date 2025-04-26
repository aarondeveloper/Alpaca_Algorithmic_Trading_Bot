import robin_stocks.robinhood as rh
import pyotp
import datetime
import time
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class RobinhoodBot:
    def __init__(self, username, password, totp_key=None):
        self.username = username
        self.password = password
        self.totp_key = totp_key
        self.logger = self._setup_logger()
        self.login()

    def _setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading_bot.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

    def login(self):
        try:
            if self.totp_key:
                totp = pyotp.TOTP(self.totp_key).now()
                rh.login(self.username, self.password, mfa_code=totp)
            else:
                rh.login(self.username, self.password)
            self.logger.info("Successfully logged in to Robinhood")
        except Exception as e:
            self.logger.error(f"Failed to log in: {str(e)}")
            raise

    def get_current_price(self, symbol):
        try:
            # Use crypto quote endpoint for Bitcoin
            price_data = rh.crypto.get_crypto_quote(symbol)
            return float(price_data['mark_price'])
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {str(e)}")
            return None

    def place_buy_order(self, symbol, amount):
        try:
            # Use crypto specific order method
            order = rh.orders.order_buy_crypto_by_price(symbol, amount)
            self.logger.info(f"Placed buy order for ${amount} worth of {symbol}")
            return order
        except Exception as e:
            self.logger.error(f"Error placing buy order for {symbol}: {str(e)}")
            return None

    def place_sell_order(self, symbol, amount):
        try:
            # Use crypto specific order method
            order = rh.orders.order_sell_crypto_by_price(symbol, amount)
            self.logger.info(f"Placed sell order for ${amount} worth of {symbol}")
            return order
        except Exception as e:
            self.logger.error(f"Error placing sell order for {symbol}: {str(e)}")
            return None

    def simple_moving_average(self, symbol, interval='day', span='week'):
        try:
            # Use crypto specific historicals
            historical_data = rh.crypto.get_crypto_historicals(symbol, interval=interval, span=span)
            prices = [float(data['close_price']) for data in historical_data]
            return sum(prices) / len(prices)
        except Exception as e:
            self.logger.error(f"Error calculating SMA for {symbol}: {str(e)}")
            return None

    def get_crypto_balance(self, symbol):
        try:
            positions = rh.crypto.get_crypto_positions()
            for position in positions:
                if position['currency']['code'] == symbol:
                    return float(position['quantity'])
            return 0.0
        except Exception as e:
            self.logger.error(f"Error getting balance for {symbol}: {str(e)}")
            return None

    def get_buying_power(self):
        try:
            profile = rh.profiles.load_account_profile()
            return float(profile['crypto_buying_power'])
        except Exception as e:
            self.logger.error(f"Error getting buying power: {str(e)}")
            return None

    def run_strategy(self, symbol, amount):
        last_trade_time = None
        last_price = None
        MIN_TRADE_INTERVAL = 120  # 2 minutes in seconds
        
        self.logger.info(f"Starting trading bot for {symbol}")
        self.logger.info(f"Trading amount: ${amount}")
        self.logger.info("Monitoring prices...")
        
        while True:
            try:
                # Check if enough time has passed since last trade
                if last_trade_time:
                    time_since_trade = time.time() - last_trade_time
                    if time_since_trade < MIN_TRADE_INTERVAL:
                        time.sleep(5)
                        continue
                    
                current_price = self.get_current_price(symbol)
                sma = self.simple_moving_average(symbol)
                buying_power = self.get_buying_power()

                if current_price and sma and buying_power is not None:
                    # Calculate price drop percentage if we have a last price
                    price_drop_percent = ((last_price - current_price) / last_price * 100) if last_price else 0
                    
                    # Log current status every iteration
                    self.logger.info(f"Current Status:")
                    self.logger.info(f"  - BTC Price: ${current_price:,.2f}")
                    self.logger.info(f"  - SMA Price: ${sma:,.2f}")
                    self.logger.info(f"  - Price vs SMA: {((current_price/sma - 1) * 100):,.2f}%")
                    if last_price:
                        self.logger.info(f"  - Price Change: {-price_drop_percent:,.2f}%")
                    self.logger.info(f"  - Buying Power: ${buying_power:,.2f}")

                    # Buy conditions
                    sma_condition = current_price < sma * 0.95
                    drop_condition = price_drop_percent >= 1.0
                    
                    if buying_power >= amount and (sma_condition or drop_condition):
                        self.logger.info("Buy conditions met!")
                        if sma_condition:
                            self.logger.info("  - Price is below 5% of SMA")
                        if drop_condition:
                            self.logger.info("  - Price dropped more than 1%")
                            
                        self.place_buy_order(symbol, amount)
                        last_trade_time = time.time()
                        self.logger.info(f"Order placed successfully")
                        self.logger.info(f"Next trade possible in {MIN_TRADE_INTERVAL/60:.1f} minutes")
                    else:
                        self.logger.info("No buy conditions met, continuing to monitor...")

                # Update last price for next iteration
                last_price = current_price
                time.sleep(10)  # Check conditions every 10 seconds
            except Exception as e:
                self.logger.error(f"Error in trading strategy: {str(e)}")
                time.sleep(60)

if __name__ == "__main__":
    # Get credentials from environment variables
    USERNAME = os.getenv('RH_USERNAME')
    PASSWORD = os.getenv('RH_PASSWORD')
    TOTP_KEY = os.getenv('RH_TOTP_KEY')

    # Trading parameters
    SYMBOL = "BTC"  # Bitcoin
    AMOUNT = 1.00  # Trading $1 worth of Bitcoin

    bot = RobinhoodBot(USERNAME, PASSWORD, TOTP_KEY)
    bot.run_strategy(SYMBOL, AMOUNT) 