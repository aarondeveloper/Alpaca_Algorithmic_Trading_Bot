import os
from alpaca.trading.client import TradingClient
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide
import time
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

class AlpacaTradingBot:
    def __init__(self):
        load_dotenv()
        
        # Initialize clients
        self.trading_client = TradingClient(
            os.getenv('ALPACA_API_KEY'), 
            os.getenv('ALPACA_SECRET_KEY'),
            paper=True  # Set to False for real trading
        )
        self.data_client = CryptoHistoricalDataClient()
        self.logger = self._setup_logger()
        
        self.logger.info("Trading bot initialized")

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

    def get_current_price(self, symbol):
        try:
            # Get the latest bar
            request = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Minute,
                start=datetime.now() - timedelta(minutes=5),
                end=datetime.now()
            )
            bars = self.data_client.get_crypto_bars(request)
            latest_bar = bars[symbol][-1]
            return latest_bar.close
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {str(e)}")
            return None

    def get_simple_moving_average(self, symbol, timeframe=TimeFrame.Hour, window=24):
        try:
            # Get historical data
            request = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=datetime.now() - timedelta(hours=window),
                end=datetime.now()
            )
            bars = self.data_client.get_crypto_bars(request)
            prices = [bar.close for bar in bars[symbol]]
            return sum(prices) / len(prices)
        except Exception as e:
            self.logger.error(f"Error calculating SMA for {symbol}: {str(e)}")
            return None

    def place_buy_order(self, symbol, amount):
        try:
            # Create market order
            order_data = MarketOrderRequest(
                symbol=symbol,
                notional=amount,  # Amount in dollars
                side=OrderSide.BUY
            )
            order = self.trading_client.submit_order(order_data)
            self.logger.info(f"Placed buy order for ${amount} of {symbol}")
            return order
        except Exception as e:
            self.logger.error(f"Error placing buy order: {str(e)}")
            return None

    def run_strategy(self, symbol, amount):
        last_trade_time = None
        last_price = None
        MIN_TRADE_INTERVAL = 120  # 2 minutes in seconds
        
        self.logger.info(f"Starting trading bot for {symbol}")
        self.logger.info(f"Trading amount: ${amount}")
        
        while True:
            try:
                # Check trading interval
                if last_trade_time and (time.time() - last_trade_time) < MIN_TRADE_INTERVAL:
                    time.sleep(5)
                    continue

                current_price = self.get_current_price(symbol)
                sma = self.get_simple_moving_average(symbol)
                account = self.trading_client.get_account()
                buying_power = float(account.buying_power)

                if current_price and sma and buying_power:
                    # Calculate price drop percentage
                    price_drop_percent = ((last_price - current_price) / last_price * 100) if last_price else 0
                    
                    # Log current status
                    self.logger.info(f"\nCurrent Status:")
                    self.logger.info(f"  - {symbol} Price: ${current_price:,.2f}")
                    self.logger.info(f"  - SMA Price: ${sma:,.2f}")
                    self.logger.info(f"  - Price vs SMA: {((current_price/sma - 1) * 100):,.2f}%")
                    if last_price:
                        self.logger.info(f"  - Price Change: {-price_drop_percent:,.2f}%")
                    self.logger.info(f"  - Buying Power: ${buying_power:,.2f}")

                    # Buy conditions
                    if buying_power >= amount and (
                        current_price < sma * 0.95 or  # Price 5% below SMA
                        price_drop_percent >= 1.0      # Price dropped 1% or more
                    ):
                        self.place_buy_order(symbol, amount)
                        last_trade_time = time.time()
                        self.logger.info("Buy order placed!")

                last_price = current_price
                time.sleep(10)

            except Exception as e:
                self.logger.error(f"Error in trading strategy: {str(e)}")
                time.sleep(60)

if __name__ == "__main__":
    # Trading parameters
    SYMBOL = "BTC/USD"
    AMOUNT = 1.00  # Trading $1 worth of Bitcoin

    bot = AlpacaTradingBot()
    bot.run_strategy(SYMBOL, AMOUNT)
