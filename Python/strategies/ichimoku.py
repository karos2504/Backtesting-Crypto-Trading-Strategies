import numpy as np
import pandas as pd

def _donchian(high: pd.Series, low: pd.Series, period: int) -> pd.Series:
    """Calculate Donchian Channel midline (used for Ichimoku components)."""
    return (high.rolling(period).max() + low.rolling(period).min()) / 2

def backtest(df: pd.DataFrame, tenkan_period: int = 9, kijun_period: int = 26) -> float:
    """
    Backtest Ichimoku Cloud strategy.
    
    Args:
        df: DataFrame with OHLCV data (columns: open, high, low, close, volume)
        tenkan_period: Tenkan-sen (conversion line) period, default 9
        kijun_period: Kijun-sen (base line) period, default 26
    
    Returns:
        Total PnL as a float
    """
    data = df.copy()
    
    # Ichimoku Components
    data['tenkan_sen'] = _donchian(data['high'], data['low'], tenkan_period)
    data['kijun_sen'] = _donchian(data['high'], data['low'], kijun_period)
    data['senkou_span_a'] = ((data['tenkan_sen'] + data['kijun_sen']) / 2).shift(kijun_period)
    data['senkou_span_b'] = _donchian(data['high'], data['low'], kijun_period * 2).shift(kijun_period)
    data['chikou_span'] = data['close'].shift(kijun_period)
    
    data.dropna(inplace=True)
    
    # Crossover Detection
    tk_diff = data['tenkan_sen'] - data['kijun_sen']
    tk_cross_up = (tk_diff > 0) & (tk_diff.shift(1) < 0)
    tk_cross_down = (tk_diff < 0) & (tk_diff.shift(1) > 0)
    
    # Cloud & Chikou Confirmation
    above_cloud = (data['close'] > data['senkou_span_a']) & (data['close'] > data['senkou_span_b'])
    below_cloud = (data['close'] < data['senkou_span_a']) & (data['close'] < data['senkou_span_b'])
    chikou_bullish = data['close'] > data['chikou_span']
    chikou_bearish = data['close'] < data['chikou_span']
    
    # Generate Signals: 1 = Buy, -1 = Sell
    data['signal'] = np.where(tk_cross_up & above_cloud & chikou_bullish, 1,
                              np.where(tk_cross_down & below_cloud & chikou_bearish, -1, 0))
    
    # Calculate PnL on signal rows only
    signals = data[data['signal'] != 0].copy()
    signals['pnl'] = signals['close'].pct_change() * signals['signal'].shift(1)
    signals['cumulative_pnl'] = (1 + signals['pnl']).cumprod()
    signals['max_cumulative_pnl'] = signals['cumulative_pnl'].cummax()
    signals['drawdown'] = (signals['cumulative_pnl'] - signals['max_cumulative_pnl']) / signals['max_cumulative_pnl']
    
    return signals['pnl'].sum(), signals['drawdown'].max()
