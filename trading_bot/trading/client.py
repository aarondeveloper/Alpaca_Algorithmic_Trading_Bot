from alpaca.trading.client import TradingClient as AlpacaClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide
from config.settings import ALPACA_API_KEY, ALPACA_SECRET_KEY, PAPER_TRADING

class AlpacaTradingClient:
    def __init__(self, logger):
        self.client = AlpacaClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=PAPER_TRADING)
        self.logger = logger

    def get_account_info(self):
        try:
            account = self.client.get_account()
            return {
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'buying_power': float(account.buying_power),
                'daily_pl': float(account.equity) - float(account.last_equity)
            }
        except Exception as e:
            self.logger.error(f"Error getting account info: {str(e)}")
            return None

    def place_buy_order(self, symbol, amount):
        try:
            self.logger.info("\nPlacing Buy Order:")
            self.logger.info(f"  Symbol: {symbol}")
            self.logger.info(f"  Amount: ${amount}")
            
            order_data = MarketOrderRequest(
                symbol=symbol,
                notional=amount,
                side=OrderSide.BUY
            )
            order = self.client.submit_order(order_data)
            
            self.logger.info("\nOrder Submitted Successfully:")
            self.logger.info(f"  Order ID: {order.id}")
            self.logger.info(f"  Status: {order.status}")
            self.logger.info(f"  Created At: {order.created_at}")
            
            return order
        except Exception as e:
            self.logger.error(f"Error placing buy order: {str(e)}")
            return None 