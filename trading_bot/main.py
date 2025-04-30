from utils.logger import setup_logger
from trading.client import AlpacaTradingClient
from trading.data import MarketData
from trading.strategy import TradingStrategy
from config.settings import SYMBOL, TRADE_AMOUNT
import time

def main():
    # Setup logger
    logger = setup_logger(__name__)
    logger.info("=" * 50)
    logger.info("TRADING BOT STARTUP")
    logger.info("=" * 50)

    # Initialize components
    trading_client = AlpacaTradingClient(logger)
    market_data = MarketData(logger)
    strategy = TradingStrategy(trading_client, market_data, logger)

    # Log initial account information
    account_info = trading_client.get_account_info()
    if account_info:
        logger.info("\nInitial Account Information:")
        logger.info(f"  Cash Balance: ${account_info['cash']:,.2f}")
        logger.info(f"  Portfolio Value: ${account_info['portfolio_value']:,.2f}")
        logger.info(f"  Buying Power: ${account_info['buying_power']:,.2f}")
        logger.info(f"  Today's P/L: ${account_info['daily_pl']:,.2f}")

    # Run the trading strategy
    logger.info("\nStarting Trading Strategy")
    logger.info(f"Trading {SYMBOL} with ${TRADE_AMOUNT} orders")

    while True:
        try:
            # Always execute to keep monitoring prices, even during cooldown
            strategy.execute(SYMBOL, TRADE_AMOUNT)
            time.sleep(30)  # Check every 30 seconds instead of 10
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            time.sleep(60)  # Wait longer on errors

if __name__ == "__main__":
    main() 