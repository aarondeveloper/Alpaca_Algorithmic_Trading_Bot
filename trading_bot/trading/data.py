from datetime import datetime, timedelta
from alpaca.data.historical.crypto import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from config.settings import SMA_WINDOW, MINUTE_SMA_WINDOW, ALPACA_API_KEY, ALPACA_SECRET_KEY
from alpaca.data.live import CryptoDataStream
from collections import deque
import asyncio
import threading

class MarketData:
    def __init__(self, logger):
        # Keep the client for hourly/daily data
        self.client = CryptoHistoricalDataClient(
            api_key=ALPACA_API_KEY,
            secret_key=ALPACA_SECRET_KEY
        )
        self.logger = logger
        # Initialize minute price history
        self.minute_closes = deque(maxlen=MINUTE_SMA_WINDOW)
        self.minute_sma = None
        self.latest_price = None
        self.latest_bar = None
        self.stream_ready = False
        
        # Start the WebSocket stream in a background thread
        self._start_crypto_stream()

    def _start_crypto_stream(self):
        """Start the WebSocket stream in a background thread"""
        self.logger.info(f"Starting WebSocket stream for real-time data (will build {MINUTE_SMA_WINDOW}-min SMA over time)...")
        
        # Define the WebSocket handlers
        async def handle_bar(bar):
            self.latest_bar = bar
            self.latest_price = bar.close
            
            # Update our minute history with this latest bar
            self.minute_closes.append(bar.close)
            # Recalculate SMA
            if len(self.minute_closes) > 0:
                self.minute_sma = sum(self.minute_closes) / len(self.minute_closes)
                self.stream_ready = True
            
            # More concise logging
            self.logger.info(f"NEW PRICE: ${bar.close:,.2f} | SMA ({len(self.minute_closes)}/{MINUTE_SMA_WINDOW}): ${self.minute_sma:,.2f}")
        
        async def handle_update(bar):
            self.latest_bar = bar
            self.latest_price = bar.close
            
            # Update the most recent price in our deque (replace the last entry)
            if len(self.minute_closes) > 0:
                self.minute_closes.pop()  # Remove the last entry
                self.minute_closes.append(bar.close)  # Add the corrected close
                self.minute_sma = sum(self.minute_closes) / len(self.minute_closes)
            
            self.logger.info(f"\n[STREAM] Bar update @ {bar.timestamp}")
            self.logger.info(f"  Corrected close: ${bar.close:,.2f}")
            self.logger.info(f"  Corrected volume: {bar.volume:,.6f}")
            self.logger.info(f"  Updated {MINUTE_SMA_WINDOW}-min SMA: ${self.minute_sma:,.2f}")
        
        # Function to run the stream in a separate thread
        def run_stream():
            stream = CryptoDataStream(ALPACA_API_KEY, ALPACA_SECRET_KEY)
            stream.subscribe_bars(handle_bar, "BTC/USD")
            stream.subscribe_updated_bars(handle_update, "BTC/USD")
            self.logger.info("WebSocket stream connected and running")
            stream.run()
        
        # Start the stream in a background thread
        stream_thread = threading.Thread(target=run_stream, daemon=True)
        stream_thread.start()
        self.logger.info("WebSocket stream thread started")

    def get_current_price(self, symbol):
        try:
            # If we have a price from the WebSocket stream, use it
            if self.stream_ready and self.latest_price is not None:
                self.logger.info("\nUsing real-time WebSocket price:")
                self.logger.info(f"  Latest price: ${self.latest_price:,.2f}")
                self.logger.info(f"  {len(self.minute_closes)}/{MINUTE_SMA_WINDOW}-min SMA: ${self.minute_sma:,.2f}")
                return self.latest_price
                
            # If WebSocket isn't ready yet, return None and wait
            self.logger.info("Waiting for WebSocket data...")
            return None
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

    def get_hourly_prices(self, symbol):
        """Get hourly price data"""
        try:
            request = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Hour,
                start=datetime.now() - timedelta(hours=24),
                end=datetime.now()
            )
            bars = self.client.get_crypto_bars(request)
            return [bar.close for bar in bars[symbol]]
        except Exception as e:
            self.logger.error(f"Error getting hourly prices: {str(e)}")
            return None

    def get_minute_sma(self, symbol: str, window: int = MINUTE_SMA_WINDOW) -> float | None:
        """Return the current SMA from our cached minute history"""
        return self.minute_sma 