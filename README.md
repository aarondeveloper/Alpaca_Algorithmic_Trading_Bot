





# Crypto Trading Bot

This project is a cryptocurrency trading bot that uses the Alpaca API to monitor Bitcoin prices and execute trades based on a strategy that looks for buying opportunities near hourly lows.

## Features

- Real-time price monitoring via WebSocket
- 500-minute Simple Moving Average (SMA) calculation
- Hourly low price analysis
- Automated trading based on technical indicators
- Paper trading support for risk-free testing

## Setup

### Prerequisites

- Python 3.8 or higher
- Alpaca API account (sign up at [alpaca.markets](https://alpaca.markets))

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/crypto-trading-bot.git
   cd crypto-trading-bot
   ```

2. Install required packages:
   ```bash
   pip install alpaca-py python-dotenv
   ```

3. Create a `.env` file in the project root with your Alpaca API credentials:
   ```
   ALPACA_API_KEY=your_api_key_here
   ALPACA_SECRET_KEY=your_secret_key_here
   ```

   You can get these credentials by signing up for an Alpaca account and creating an API key in your dashboard.

## Configuration

Edit `trading_bot/config/settings.py` to customize your trading parameters:

- `SYMBOL`: The cryptocurrency pair to trade (default: "BTC/USD")
- `TRADE_AMOUNT`: Dollar amount per trade (default: $10.00)
- `MIN_TRADE_INTERVAL`: Minimum time between trades in seconds (default: 120)
- `MINUTE_SMA_WINDOW`: Number of minutes for SMA calculation (default: 500)

## Running the Bot

To start the trading bot:

```bash
python -m trading_bot.main
```

The bot will:
1. Connect to Alpaca's WebSocket for real-time price data
2. Build a 500-minute SMA over time
3. Analyze hourly price patterns
4. Place buy orders when conditions are favorable

## Test Scripts

### Testing Market Orders

To test if your Alpaca API credentials can place orders:

```bash
python -m trading_bot.place_market_order_test
```

This will attempt to place a $10 buy order for BTC/USD using your API credentials.

### Testing Data Stream

To test the WebSocket connection and see real-time price data:

```bash
python -m trading_bot.data_stream_test
```

This will display real-time minute bars, daily bars, and any corrections to the most recent bar.

## Trading Strategy

The bot uses a strategy that looks for buying opportunities when:

1. The current price is within 0.5% of the current hour's low
2. AND EITHER:
   - Hourly lows are dropping (current hour's low is lower than previous hour's)
   - OR a local minimum is detected in recent price history

This strategy aims to "buy the dip" by identifying potential reversal points.

## Logs

The bot creates a date-stamped log file (`trading_bot_YYYY-MM-DD.log`) that records all activity, including:
- Price updates
- SMA calculations
- Trading signals
- Order placements
- Errors

## Disclaimer

This trading bot is for educational purposes only. Use at your own risk. Cryptocurrency trading involves substantial risk of loss and is not suitable for all investors.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
