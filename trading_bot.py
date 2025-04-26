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

    def run_strategy(self, symbol, amount):
        while True:
            try:
                current_price = self.get_current_price(symbol)
                sma = self.simple_moving_average(symbol)

                if current_price and sma:
                    if current_price < sma * 0.95:  # Buy if price is 5% below SMA
                        self.place_buy_order(symbol, amount)
                    elif current_price > sma * 1.05:  # Sell if price is 5% above SMA
                        self.place_sell_order(symbol, amount)

                time.sleep(60)  # Wait for 1 minute before next check
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