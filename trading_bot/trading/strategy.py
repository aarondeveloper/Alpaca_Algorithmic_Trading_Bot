import time
from config.settings import (
    MIN_TRADE_INTERVAL, 
    SMA_THRESHOLD, 
    PRICE_DROP_THRESHOLD
)

class TradingStrategy:
    def __init__(self, trading_client, market_data, logger):
        self.trading_client = trading_client
        self.market_data = market_data
        self.logger = logger
        self.last_trade_time = None
        self.last_price = None

    def log_market_analysis(self, symbol, current_price, sma, buying_power):
        price_drop_percent = ((self.last_price - current_price) / self.last_price * 100) if self.last_price else 0
        price_vs_sma_percent = ((current_price/sma - 1) * 100)
        
        self.logger.info("\n" + "="*30)
        self.logger.info("Market Analysis:")
        self.logger.info(f"  Current Price: ${current_price:,.2f}")
        self.logger.info(f"  24h SMA: ${sma:,.2f}")
        self.logger.info(f"  Price vs SMA: {price_vs_sma_percent:,.2f}%")
        if self.last_price:
            self.logger.info(f"  Price Change: {-price_drop_percent:,.2f}%")
        self.logger.info(f"  Buying Power: ${buying_power:,.2f}")
        
        return price_drop_percent, price_vs_sma_percent

    def should_buy(self, current_price, sma, price_drop_percent):
        sma_condition = current_price < sma * SMA_THRESHOLD
        drop_condition = price_drop_percent >= PRICE_DROP_THRESHOLD

        self.logger.info("\nBuy Conditions:")
        self.logger.info(f"  Below SMA: {sma_condition}")
        self.logger.info(f"  Price Drop: {drop_condition}")

        return sma_condition or drop_condition

    def execute(self, symbol, amount):
        try:
            if self.last_trade_time:
                time_since_last_trade = time.time() - self.last_trade_time
                if time_since_last_trade < MIN_TRADE_INTERVAL:
                    return False

            current_price = self.market_data.get_current_price(symbol)
            sma = self.market_data.get_simple_moving_average(symbol)
            account_info = self.trading_client.get_account_info()
            
            if not all([current_price, sma, account_info]):
                return False

            buying_power = account_info['buying_power']
            price_drop_percent, _ = self.log_market_analysis(
                symbol, current_price, sma, buying_power
            )

            if buying_power >= amount and self.should_buy(current_price, sma, price_drop_percent):
                self.logger.info("\n*** BUY SIGNAL DETECTED ***")
                order = self.trading_client.place_buy_order(symbol, amount)
                if order:
                    self.last_trade_time = time.time()
                    self.logger.info(f"Next trade possible in: {MIN_TRADE_INTERVAL/60:.1f} minutes")
            else:
                self.logger.info("\nNo buy signals detected")

            self.last_price = current_price
            return True

        except Exception as e:
            self.logger.error(f"\nError in trading strategy: {str(e)}")
            return False 