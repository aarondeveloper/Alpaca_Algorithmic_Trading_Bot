import os
import logging
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()

# Load environment variables
load_dotenv()
API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv('ALPACA_SECRET_KEY')

def place_market_order(symbol, amount, side="buy"):
    """
    Place a market order for the specified symbol and amount.
    
    Args:
        symbol (str): The trading symbol (e.g., "BTC/USD")
        amount (float): Dollar amount to trade
        side (str): "buy" or "sell"
    
    Returns:
        The order object if successful, None otherwise
    """
    try:
        logger.info(f"Placing {side} order for ${amount} of {symbol}")
        
        # Initialize the client
        client = TradingClient(API_KEY, API_SECRET, paper=True)
        
        # Create the order request
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            notional=amount,  # Dollar amount
            side=order_side,
            time_in_force=TimeInForce.GTC
        )
        
        # Submit the order
        order = client.submit_order(market_order_data)
        
        if order:
            logger.info(f"Order placed successfully!")
            logger.info(f"Order ID: {order.id}")
            logger.info(f"Status: {order.status}")
            logger.info(f"Created at: {order.created_at}")
            return order
        
        return None
    
    except Exception as e:
        logger.error(f"Error placing order: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usage
    symbol = "BTC/USD"
    amount = 10.00  # $10 USD
    
    # Place a buy order
    order = place_market_order(symbol, amount, "buy")
    
    if order:
        logger.info("Test completed successfully")
    else:
        logger.error("Test failed")
