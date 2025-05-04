from alpaca.trading.client import TradingClient as AlpacaClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical.crypto import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from config.settings import ALPACA_API_KEY, ALPACA_SECRET_KEY, PAPER_TRADING

class AlpacaTradingClient:
    def __init__(self, logger):
        self.client = AlpacaClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=PAPER_TRADING)
        self.data_client = CryptoHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)
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
        """Place a market buy order"""
        try:
            self.logger.info(f"PLACING ORDER: ${amount} of {symbol}")
            
            # Create a market order request object
            market_order_data = MarketOrderRequest(
                symbol=symbol,
                notional=amount,  # Convert dollar amount to quantity
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC
            )
            
            # Submit the order using the approach from the video
            order = self.client.submit_order(market_order_data)
            
            if order:
                self.logger.info(f"ORDER PLACED: ID {order.id} | Status: {order.status}")
                return order
            return None
        except Exception as e:
            self.logger.error(f"Error placing buy order: {str(e)}")
            return None

    def get_hourly_bars(self, symbol, limit=24):
        """Get hourly bars for the specified symbol"""
        try:
            # Calculate start time based on limit
            start_time = datetime.now() - timedelta(hours=limit)
            
            request = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Hour,
                start=start_time,
                end=datetime.now()
            )
            
            bars_response = self.data_client.get_crypto_bars(request)
            
            # Convert to list and return
            return list(bars_response[symbol])
        except Exception as e:
            self.logger.error(f"Error getting hourly bars: {str(e)}")
            return [] 