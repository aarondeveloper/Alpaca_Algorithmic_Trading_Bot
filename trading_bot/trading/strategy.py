import time
from datetime import datetime, timedelta
from config.settings import MIN_TRADE_INTERVAL, MINUTE_SMA_WINDOW

class TradingStrategy:
    def __init__(self, trading_client, market_data, logger):
        self.trading_client = trading_client
        self.market_data = market_data
        self.logger = logger
        self.last_trade_time = None
        self.last_price = None
        self.price_history = []  # Store recent minute prices
        self.hourly_lows = []   # Store hourly lows
        self.in_cooldown = False

    def analyze_hourly_pattern(self, current_price):
        """Analyze hourly price patterns"""
        try:
            hourly_prices = self.market_data.get_hourly_prices("BTC/USD")
            if not hourly_prices:
                return None, None, None  # Return three None values

            # Calculate hourly lows for the last 24 hours
            self.hourly_lows = []
            for i in range(0, len(hourly_prices), 1):
                self.hourly_lows.append(min(hourly_prices[i:i+1]))

            # Get recent low prices
            last_hour_low = self.hourly_lows[-1] if self.hourly_lows else current_price
            prev_hour_low = self.hourly_lows[-2] if len(self.hourly_lows) > 1 else last_hour_low
            
            # Calculate price metrics
            price_from_hour_low = ((current_price - last_hour_low) / last_hour_low) * 100
            hour_low_change = ((last_hour_low - prev_hour_low) / prev_hour_low) * 100

            # Calculate average hourly low
            avg_hourly_low = sum(self.hourly_lows) / len(self.hourly_lows)

            # More concise hourly analysis logging
            self.logger.info(f"Hourly: Price ${current_price:,.2f} | Current Low ${last_hour_low:,.2f} | " +
                            f"Prev Low ${prev_hour_low:,.2f} | +{price_from_hour_low:.2f}% from low | " +
                            f"Low change {hour_low_change:.2f}% | 24h Avg ${avg_hourly_low:.2f}")

            return last_hour_low, price_from_hour_low, hour_low_change

        except Exception as e:
            self.logger.error(f"Error in hourly analysis: {str(e)}")
            return None, None, None

    def is_local_minimum(self, prices, center_idx, window=5):
        """Check if price point is a local minimum within window"""
        if len(prices) < window or center_idx < window//2 or center_idx >= len(prices) - window//2:
            return False
        
        center_price = prices[center_idx]
        left_prices = prices[center_idx - window//2:center_idx]
        right_prices = prices[center_idx + 1:center_idx + window//2 + 1]
        
        return all(center_price <= p for p in left_prices) and all(center_price <= p for p in right_prices)

    def should_buy(self, current_price):
        """Determine if we should buy based on hourly lows analysis"""
        # Add current price to history
        self.price_history.append(current_price)
        if len(self.price_history) > 30:  # Keep last 30 minute prices
            self.price_history.pop(0)

        # Get hourly analysis
        hour_low, price_from_hour_low, hour_low_change = self.analyze_hourly_pattern(current_price)
        if hour_low is None:
            return False

        # Check for local minimum in recent prices
        is_local_min = False
        if len(self.price_history) >= 5:
            is_local_min = self.is_local_minimum(
                self.price_history, 
                len(self.price_history) - 3
            )

        # Buying conditions
        price_near_hour_low = price_from_hour_low <= 0.5  # Within 0.5% of hour's low
        hourly_lows_dropping = hour_low_change < -0.1  # Hour's low is dropping
        found_local_minimum = is_local_min

        self.logger.info("\nBuy Signal Analysis:")
        self.logger.info(f"  Near Hour's Low: {price_near_hour_low}")
        self.logger.info(f"  Hourly Lows Dropping: {hourly_lows_dropping}")
        self.logger.info(f"  Local Minimum Found: {found_local_minimum}")

        # Buy if price is near hour's low AND either:
        # 1. Hourly lows are dropping (catching a dip)
        # 2. OR we found a local minimum
        return price_near_hour_low and (hourly_lows_dropping or found_local_minimum)

    def execute(self, symbol, amount):
        try:
            # Check if we're in the cooldown period
            if self.last_trade_time:
                elapsed = time.time() - self.last_trade_time
                if elapsed < MIN_TRADE_INTERVAL:
                    self.in_cooldown = True
                    remaining = MIN_TRADE_INTERVAL - elapsed
                    # Only log cooldown status every 30 seconds
                    if int(remaining) % 30 == 0 or remaining < 10:
                        self.logger.info(f"In trade cooldown: {remaining:.1f} seconds remaining")
                else:
                    # Cooldown period is over
                    if self.in_cooldown:
                        self.logger.info("Cooldown period ended, can place trades again")
                        self.in_cooldown = False

            current_price = self.market_data.get_current_price(symbol)
            # Get the cached 500-bar SMA (already updated in get_current_price)
            minute_sma = self.market_data.get_minute_sma(symbol)

            account_info = self.trading_client.get_account_info()
            if not all([current_price, account_info]):
                return False

            buying_power = account_info['buying_power']

            if buying_power >= amount and self.should_buy(current_price) and not self.in_cooldown:
                self.logger.info("\n*** HOURLY LOW BUYING OPPORTUNITY ***")
                order = self.trading_client.place_buy_order(symbol, amount)
                if order:
                    self.last_trade_time = time.time()
                    self.logger.info(f"Next trade possible in: {MIN_TRADE_INTERVAL/60:.1f} minutes")
            else:
                self.logger.info("\nWaiting for better hourly low entry")

            self.last_price = current_price
            return True

        except Exception as e:
            self.logger.error(f"\nError in trading strategy: {str(e)}")
            return False 