import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, '..', '..', 'logs')
DATA_DIR = os.path.join(BASE_DIR, '..', '..', 'data')

# Create directories if they don't exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Constants
TIMEFRAMES = {
    '1m': '1min',
    '5m': '5min',
    '15m': '15min',
    '30m': '30min',
    '1h': '1h',
    '4h': '4h',
    '1d': '1D',
    '1w': '1W',
    '1M': '1ME',
}

TIMEFRAME_OPTIONS = list(TIMEFRAMES.keys())

STRATEGIES = ['obv', 'ichimoku', 'support_resistance', 'sma', 'psar']

EXCHANGES = ['binance', 'okx']
