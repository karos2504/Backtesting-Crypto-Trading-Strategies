"""Parabolic SAR Strategy"""
import numpy as np
import pandas as pd
from typing import Tuple


def _calculate_psar(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                    initial_af: float, max_af: float, increment: float) -> np.ndarray:
    """Calculate Parabolic SAR values."""
    n = len(close)
    psar = np.zeros(n)
    trend = np.zeros(n, dtype=int)
    af = np.full(n, initial_af)
    ep = np.zeros(n)
    
    # Initialize
    trend[0] = 1 if close[1] > close[0] else -1
    psar[0] = low[0] if trend[0] > 0 else high[0]
    ep[0] = high[0] if trend[0] > 0 else low[0]
    
    for i in range(1, n):
        # Calculate new PSAR
        psar[i] = psar[i-1] + af[i-1] * (ep[i-1] - psar[i-1])
        
        # Check for trend reversal
        if trend[i-1] > 0:
            psar[i] = min(psar[i], low[i-1], low[i-2] if i > 1 else low[i-1])
            if low[i] < psar[i]:
                trend[i] = -1
                psar[i] = ep[i-1]
                ep[i] = low[i]
                af[i] = initial_af
            else:
                trend[i] = trend[i-1]
                ep[i] = max(ep[i-1], high[i])
                af[i] = min(max_af, af[i-1] + increment) if ep[i] > ep[i-1] else af[i-1]
        else:
            psar[i] = max(psar[i], high[i-1], high[i-2] if i > 1 else high[i-1])
            if high[i] > psar[i]:
                trend[i] = 1
                psar[i] = ep[i-1]
                ep[i] = high[i]
                af[i] = initial_af
            else:
                trend[i] = trend[i-1]
                ep[i] = min(ep[i-1], low[i])
                af[i] = min(max_af, af[i-1] + increment) if ep[i] < ep[i-1] else af[i-1]
    
    return trend


def backtest(df: pd.DataFrame, initial_af: float = 0.02, 
             max_af: float = 0.2, increment: float = 0.02) -> Tuple[float, float]:
    """
    Backtest Parabolic SAR strategy.
    
    Args:
        df: DataFrame with OHLCV data
        initial_af: Initial acceleration factor
        max_af: Maximum acceleration factor
        increment: AF increment step
    
    Returns:
        Tuple of (total_pnl%, max_drawdown%)
    """
    data = df.copy()
    
    if len(data) < 3:
        return 0.0, 0.0
    
    high = data['high'].values
    low = data['low'].values
    close = data['close'].values
    
    # Calculate PSAR trend
    trend = _calculate_psar(high, low, close, initial_af, max_af, increment)
    data['signal'] = trend
    
    # Calculate returns
    data['pnl'] = data['close'].pct_change() * data['signal'].shift(1)
    data['cumulative'] = (1 + data['pnl']).cumprod()
    data['max_cumulative'] = data['cumulative'].cummax()
    data['drawdown'] = (data['cumulative'] - data['max_cumulative']) / data['max_cumulative']
    
    total_pnl = data['pnl'].sum() * 100
    max_drawdown = abs(data['drawdown'].min()) * 100
    
    return total_pnl, max_drawdown
