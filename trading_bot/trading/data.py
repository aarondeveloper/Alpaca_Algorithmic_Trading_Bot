from datetime import datetime, timedelta
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from config.settings import SMA_WINDOW

class MarketData:
    def __init__(self, logger):
        self.client = CryptoHistoricalDataClient()
        self.logger = logger

    def get_current_price(self, symbol):
        try:
            request = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Minute,
                start=datetime.now() - timedelta(minutes=5),
                end=datetime.now()
            )
            bars = self.client.get_crypto_bars(request)
            latest_bar = bars[symbol][-1]
            
            # Log more detailed price information
            self.logger.info("\nLatest Bar Data:")
            self.logger.info(f"  Open: ${latest_bar.open:,.2f}")
            self.logger.info(f"  High: ${latest_bar.high:,.2f}")
            self.logger.info(f"  Low: ${latest_bar.low:,.2f}")
            self.logger.info(f"  Close: ${latest_bar.close:,.2f}")
            self.logger.info(f"  Volume: {latest_bar.volume:,.2f}")
            
            return latest_bar.close
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {str(e)}")
            return None

    def get_simple_moving_average(self, symbol):
        try:
            # Get 24-hour data in hourly bars
            request = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Hour,
                start=datetime.now() - timedelta(hours=SMA_WINDOW),
                end=datetime.now()
            )
            bars = self.client.get_crypto_bars(request)
            prices = [bar.close for bar in bars[symbol]]
            
            # Log more detailed SMA information
            self.logger.info("\nSMA Analysis:")
            self.logger.info(f"  Number of periods: {len(prices)}")
            self.logger.info(f"  Highest price: ${max(prices):,.2f}")
            self.logger.info(f"  Lowest price: ${min(prices):,.2f}")
            self.logger.info(f"  Average volume: {sum([bar.volume for bar in bars[symbol]])/len(bars[symbol]):,.2f}")
            
            return sum(prices) / len(prices)
        except Exception as e:
            self.logger.error(f"Error calculating SMA for {symbol}: {str(e)}")
            return None

    def get_daily_price_range(self, symbol):
        """Get 24-hour price range"""
        try:
            request = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Hour,
                start=datetime.now() - timedelta(hours=24),
                end=datetime.now()
            )
            bars = self.client.get_crypto_bars(request)
            prices = [bar.close for bar in bars[symbol]]
            
            self.logger.info("\n24-Hour Range:")
            self.logger.info(f"  High: ${max(prices):,.2f}")
            self.logger.info(f"  Low: ${min(prices):,.2f}")
            self.logger.info(f"  Range: ${max(prices) - min(prices):,.2f}")
            
            return min(prices), max(prices)
        except Exception as e:
            self.logger.error(f"Error getting daily range: {str(e)}")
            return None 