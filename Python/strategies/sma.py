"""SMA Crossover Strategy"""
import numpy as np
import pandas as pd
from typing import Tuple


def backtest(df: pd.DataFrame, fast_ma: int = 9, slow_ma: int = 26) -> Tuple[float, float]:
    """
    Backtest Simple Moving Average crossover strategy.
    
    Args:
        df: DataFrame with OHLCV data
        fast_ma: Fast moving average period
        slow_ma: Slow moving average period
    
    Returns:
        Tuple of (total_pnl%, max_drawdown%)
    """
    data = df.copy()
    
    # Calculate moving averages
    data['fast_ma'] = data['close'].rolling(window=fast_ma).mean()
    data['slow_ma'] = data['close'].rolling(window=slow_ma).mean()
    data.dropna(inplace=True)
    
    if len(data) < 2:
        return 0.0, 0.0
    
    # Generate signals: 1 = long, -1 = short
    data['signal'] = np.where(data['fast_ma'] > data['slow_ma'], 1, -1)
    
    # Calculate returns
    data['pnl'] = data['close'].pct_change() * data['signal'].shift(1)
    data['cumulative'] = (1 + data['pnl']).cumprod()
    data['max_cumulative'] = data['cumulative'].cummax()
    data['drawdown'] = (data['cumulative'] - data['max_cumulative']) / data['max_cumulative']
    
    total_pnl = data['pnl'].sum() * 100
    max_drawdown = abs(data['drawdown'].min()) * 100
    
    return total_pnl, max_drawdown
