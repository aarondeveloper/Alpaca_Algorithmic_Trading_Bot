# test.py
import logging
from trading_bot.trading.client import AlpacaTradingClient
from trading_bot.config.settings import SYMBOL, TRADE_AMOUNT

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger()

def test_place_buy_order():
    """Test if place_buy_order works correctly"""
    logger.info("=== TESTING PLACE BUY ORDER ===")
    
    # Initialize the trading client
    client = AlpacaTradingClient(logger)
    
    # Try to place a buy order
    logger.info(f"Attempting to place a buy order for {SYMBOL} with amount ${TRADE_AMOUNT}")
    order = client.place_buy_order(SYMBOL, TRADE_AMOUNT)
    
    # Check the result
    if order:
        logger.info(f"SUCCESS: Order placed successfully")
        logger.info(f"Order ID: {order.id}")
        logger.info(f"Status: {order.status}")
        logger.info(f"Created At: {order.created_at}")
        return True
    else:
        logger.error("FAILED: Could not place order")
        return False

if __name__ == "__main__":
    test_place_buy_order()