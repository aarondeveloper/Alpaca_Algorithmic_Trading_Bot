import os
from dotenv import load_dotenv
from alpaca.data.live import CryptoDataStream

# pull in your ALPACA_API_KEY / ALPACA_SECRET_KEY from .env
load_dotenv()

API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv('ALPACA_SECRET_KEY')

async def handle_bar(bar):
    print(f"[BAR]    {bar.symbol} @ {bar.timestamp}   Open:{bar.open} High:{bar.high} Low:{bar.low} Close:{bar.close}")

async def handle_daily(bar):
    print(f"[DAILY]  {bar.symbol}   Open:{bar.open} High:{bar.high} Low:{bar.low} Close:{bar.close} Volume:{bar.volume}")

async def handle_update(bar):
    print(f"[UPDATE] corrected {bar.symbol} @ {bar.timestamp}  New Close:{bar.close}, Volume:{bar.volume}")

def main():
    # CryptoDataStream for BTC/USD
    stream = CryptoDataStream(API_KEY, API_SECRET)

    # 1. Standard minute bars (one per minute, right after each minute)
    stream.subscribe_bars(handle_bar, "BTC/USD")

    # 2. Corrections to the most recent minute bar (if late trades arrive)
    stream.subscribe_updated_bars(handle_update, "BTC/USD")

    # 3. Daily bars (once per day)
    stream.subscribe_daily_bars(handle_daily, "BTC/USD")

    # this will spin up its own asyncio loop internally
    stream.run()

if __name__ == "__main__":
    main()