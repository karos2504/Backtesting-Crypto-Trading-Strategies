import typing
import pandas as pd
import pandas_ta as ta

from .base import AbstractStrategy

class ObvStrategy(AbstractStrategy):
    def __init__(self):
        super().__init__()
        self.params = {
            'ma_period': {'name': 'MA Period', 'type': int, 'default': 9, 'min': 1, 'max': 200}
        }

    def backtest(self, df: pd.DataFrame, **kwargs) -> typing.Tuple[float, float]:
        ma_period = kwargs.get('ma_period', self.params['ma_period']['default'])
        
        df = df.copy()
        df['obv'] = ta.obv(df['close'], df['volume'])
        df['obv_ma'] = ta.sma(df['obv'], length=ma_period)
        
        df['signal'] = 0
        df.loc[df['obv'] > df['obv_ma'], 'signal'] = 1
        df.loc[df['obv'] <= df['obv_ma'], 'signal'] = -1

        df['pnl'] = df['close'].pct_change() * df['signal'].shift(1)
        df['cumulative_pnl'] = (1 + df['pnl']).cumprod()
        df['max_cumulative_pnl'] = df['cumulative_pnl'].cummax()
        df['drawdown'] = (df['cumulative_pnl'] - df['max_cumulative_pnl']) / df['max_cumulative_pnl']
        
        return df['pnl'].sum(), df['drawdown'].max()