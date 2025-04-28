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
            return latest_bar.close
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {str(e)}")
            return None

    def get_simple_moving_average(self, symbol):
        try:
            request = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Hour,
                start=datetime.now() - timedelta(hours=SMA_WINDOW),
                end=datetime.now()
            )
            bars = self.client.get_crypto_bars(request)
            prices = [bar.close for bar in bars[symbol]]
            return sum(prices) / len(prices)
        except Exception as e:
            self.logger.error(f"Error calculating SMA for {symbol}: {str(e)}")
            return None 