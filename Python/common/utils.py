import datetime
import pandas as pd

from common.config import TIMEFRAMES

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
