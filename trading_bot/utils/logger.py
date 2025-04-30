import logging
import os
import glob
from datetime import datetime

def setup_logger(name):
    # Create a log filename with today's date
    today = datetime.now().strftime('%Y-%m-%d')
    log_filename = f'trading_bot_{today}.log'
    
    # Delete old log files (from previous days)
    old_logs = glob.glob('trading_bot_*.log')
    for old_log in old_logs:
        # Skip today's log file
        if old_log != log_filename:
            try:
                os.remove(old_log)
                print(f"Deleted old log file: {old_log}")
            except Exception as e:
                print(f"Could not delete {old_log}: {e}")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(name) 