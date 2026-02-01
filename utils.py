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