import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
PAPER_TRADING = True

# Trading Parameters
SYMBOL = "BTC/USD"
TRADE_AMOUNT = 10.00  # Minimum $10 for crypto
MIN_TRADE_INTERVAL = 120  # 2 minutes

# Strategy Parameters
SMA_WINDOW = 24  # hours
SMA_THRESHOLD = 0.95  # 5% below SMA
PRICE_DROP_THRESHOLD = 1.0  # 1% price drop

# How many 1-minute bars to use for our SMA
MINUTE_SMA_WINDOW = 500 