import datetime
import pandas as pd

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

STRATEGIES = {
    'obv': {
        'ma_period': {'name': 'MA Period', 'type': int, 'default': 9}
    },

    'ichimoku': {
        'tenkan_period': {'name': 'Tenkan Period', 'type': int, 'default': 9},
        'kijun_period': {'name': 'Kijun Period', 'type': int, 'default': 26}
    },

    'support_resistance': {
        'min_points': {'name': 'Min Points', 'type': int, 'default': 3},
        'min_diff_points': {'name': 'Min Difference between touches', 'type': int, 'default': 7},
        'rounding_nb': {'name': 'Rounding', 'type': int, 'default': 200},
        'take_profit': {'name': 'Take Profit', 'type': int, 'default': 10},
        'stop_loss': {'name': 'Stop Loss', 'type': int, 'default': 5}
    },
    'sma': {
        'fast_ma': {'name': 'Fast MA', 'type': int, 'default': 9},
        'slow_ma': {'name': 'Slow MA', 'type': int, 'default': 26}
    },
    'psar': {
        'initial_af': {'name': 'Initial AF', 'type': float, 'default': 0.02},
        'max_af': {'name': 'Max AF', 'type': float, 'default': 0.2},
        'increment': {'name': 'Increment', 'type': float, 'default': 0.02}
    }
}

def ms_to_datetime(ms: int):
    return datetime.datetime.fromtimestamp(ms / 1000)

def resample_timeframe(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    return df.resample(TIMEFRAMES[timeframe]).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })