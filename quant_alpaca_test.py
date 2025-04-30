#!/usr/bin/env python3
import os
from datetime import datetime
import QuantLib as ql
from dotenv import load_dotenv
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.live import CryptoDataStream

# 1) Load API keys from .env
load_dotenv()
API_KEY    = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")
SYMBOL     = "BTC/USD"

if not API_KEY or not API_SECRET:
    raise SystemExit("❌  Please set ALPACA_API_KEY and ALPACA_SECRET_KEY in your .env")

# 2) Fetch historical 1-minute bars (last 500)
hist_client = CryptoHistoricalDataClient(api_key=API_KEY, secret_key=API_SECRET)
req = CryptoBarsRequest(
    symbol_or_symbols=[SYMBOL],
    timeframe=TimeFrame.Minute,
    limit=500
)
bars = hist_client.get_crypto_bars(req)
historical_bars = bars[SYMBOL] if SYMBOL in bars else []
print(f"\n✅ Fetched {len(historical_bars)} historical bars for {SYMBOL}\n")

# 3) Build a simple in-memory map of close-quotes (dict[ql.Date → ql.SimpleQuote])
ts = {}
for bar in historical_bars:
    dt = bar.timestamp               # Python datetime
    qd = ql.Date(dt.day, dt.month, dt.year)
    ts[qd] = ql.SimpleQuote(float(bar.close))

print("🕒  QuantLib TimeSeries initialized with historical closes.\n")

# 4) Define stream handlers
async def handle_bar(bar):
    dt  = bar.timestamp
    qd  = ql.Date(dt.day, dt.month, dt.year)
    ts[qd] = ql.SimpleQuote(float(bar.close))
    print(f"[STREAM BAR]    {bar.symbol} @ {bar.timestamp}   O:{bar.open:.2f} H:{bar.high:.2f} L:{bar.low:.2f} C:{bar.close:.2f}")

async def handle_update(bar):
    dt  = bar.timestamp
    qd  = ql.Date(dt.day, dt.month, dt.year)
    ts[qd] = ql.SimpleQuote(float(bar.close))
    print(f"[STREAM UPDATE] corrected {bar.symbol} @ {bar.timestamp}  New C:{bar.close:.2f}, Vol:{bar.volume}")

async def handle_daily(bar):
    print(f"[DAILY BAR]      {bar.symbol} @ {bar.timestamp.date()}  Close:{bar.close:.2f}  Vol:{bar.volume}")

# 5) Wire up the CryptoDataStream
stream = CryptoDataStream(api_key=API_KEY, secret_key=API_SECRET)
stream.subscribe_bars(handle_bar,           SYMBOL)
stream.subscribe_updated_bars(handle_update, SYMBOL)
stream.subscribe_daily_bars(handle_daily,    SYMBOL)

# 6) Run the stream (blocks internally)
if __name__ == "__main__":
    try:
        print("▶️  Starting CryptoDataStream…\n")
        stream.run()
    except Exception as e:
        print("❌ Stream died with error:", e)
