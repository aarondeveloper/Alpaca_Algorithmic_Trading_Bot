import time
from datetime import datetime, timedelta
from config.settings import MIN_TRADE_INTERVAL

class TradingStrategy:
    def __init__(self, trading_client, market_data, logger):
        self.trading_client = trading_client
        self.market_data = market_data
        self.logger = logger
        self.last_trade_time = None
        self.last_price = None
        self.price_history = []  # Store recent prices
        self.local_lows = []    # Store local minimum prices

    def is_local_minimum(self, prices, center_idx, window=5):
        """Check if price point is a local minimum within window"""
        if len(prices) < window or center_idx < window//2 or center_idx >= len(prices) - window//2:
            return False
        
        center_price = prices[center_idx]
        left_prices = prices[center_idx - window//2:center_idx]
        right_prices = prices[center_idx + 1:center_idx + window//2 + 1]
        
        # Check if center price is lower than surrounding prices
        return all(center_price <= p for p in left_prices) and all(center_price <= p for p in right_prices)

    def analyze_price_levels(self, current_price):
        """Analyze different timeframe support levels"""
        daily_low, daily_high = self.market_data.get_daily_price_range("BTC/USD")
        hourly_data = self.market_data.get_hourly_prices("BTC/USD")
        
        # Calculate price position
        daily_range = daily_high - daily_low
        price_from_low = ((current_price - daily_low) / daily_range) * 100
        
        self.logger.info("\nPrice Level Analysis:")
        self.logger.info(f"  24h High: ${daily_high:,.2f}")
        self.logger.info(f"  24h Low: ${daily_low:,.2f}")
        self.logger.info(f"  Current price is {price_from_low:.1f}% above daily low")
        
        return daily_low, daily_high, price_from_low

    def should_buy(self, current_price, price_from_low):
        """Determine if we should buy based on dip analysis"""
        # Add current price to history
        self.price_history.append(current_price)
        if len(self.price_history) > 30:  # Keep last 30 prices
            self.price_history.pop(0)

        # Check for local minimum
        is_local_min = False
        if len(self.price_history) >= 5:
            is_local_min = self.is_local_minimum(
                self.price_history, 
                len(self.price_history) - 3  # Check if recent price was minimum
            )
            if is_local_min:
                self.local_lows.append(current_price)
                if len(self.local_lows) > 5:  # Keep last 5 local lows
                    self.local_lows.pop(0)

        # Buying conditions
        price_near_daily_low = price_from_low <= 20  # Within 20% of daily low
        found_local_minimum = is_local_min
        trending_higher_lows = (len(self.local_lows) >= 2 and 
                              self.local_lows[-1] > self.local_lows[0])

        self.logger.info("\nBuy Signal Analysis:")
        self.logger.info(f"  Near Daily Low: {price_near_daily_low}")
        self.logger.info(f"  Local Minimum Found: {found_local_minimum}")
        self.logger.info(f"  Higher Lows Trend: {trending_higher_lows}")

        # Buy if price is near daily low OR we found a local minimum
        return price_near_daily_low or (found_local_minimum and trending_higher_lows)

    def execute(self, symbol, amount):
        try:
            if self.last_trade_time:
                time_since_last_trade = time.time() - self.last_trade_time
                if time_since_last_trade < MIN_TRADE_INTERVAL:
                    return False

            current_price = self.market_data.get_current_price(symbol)
            account_info = self.trading_client.get_account_info()
            
            if not all([current_price, account_info]):
                return False

            buying_power = account_info['buying_power']
            daily_low, daily_high, price_from_low = self.analyze_price_levels(current_price)

            if buying_power >= amount and self.should_buy(current_price, price_from_low):
                self.logger.info("\n*** DIP BUYING OPPORTUNITY DETECTED ***")
                if price_from_low <= 20:
                    self.logger.info("Reason: Price near daily low - good value buy")
                else:
                    self.logger.info("Reason: Local minimum detected with higher lows trend")
                
                order = self.trading_client.place_buy_order(symbol, amount)
                if order:
                    self.last_trade_time = time.time()
                    self.logger.info(f"Next trade possible in: {MIN_TRADE_INTERVAL/60:.1f} minutes")
            else:
                self.logger.info("\nWaiting for better dip buying opportunity")

            self.last_price = current_price
            return True

        except Exception as e:
            self.logger.error(f"\nError in trading strategy: {str(e)}")
            return False 