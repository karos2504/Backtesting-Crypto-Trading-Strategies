import numpy as np
import pandas as pd
import pandas_ta as ta

def backtest(df: pd.DataFrame, ma_period: int) -> pd.DataFrame:
    
    df['obv'] = ta.obv(df['close'], df['volume'])
    df['obv_ma'] = ta.sma(df['obv'], length=ma_period)
    
    df['signal'] = np.where(df['obv'] > df['obv_ma'], 1, -1)
    df['pnl'] = df['close'].pct_change() * df['signal'].shift(1)
    df['cumulative_pnl'] = (1 + df['pnl']).cumprod()
    df['max_cumulative_pnl'] = df['cumulative_pnl'].cummax()
    df['drawdown'] = (df['cumulative_pnl'] - df['max_cumulative_pnl']) / df['max_cumulative_pnl']
    
    return df['pnl'].sum(), df['drawdown'].max()