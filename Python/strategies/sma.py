"""SMA Crossover Strategy"""
import numpy as np
import pandas as pd
import typing
from typing import Tuple

from .base import AbstractStrategy

class SmaStrategy(AbstractStrategy):
    def __init__(self):
        super().__init__()
        self.params = {
            'fast_ma': {'name': 'Fast MA', 'type': int, 'default': 9, 'min': 1, 'max': 200},
            'slow_ma': {'name': 'Slow MA', 'type': int, 'default': 26, 'min': 1, 'max': 200}
        }

    def validate_params(self, params: typing.Dict) -> typing.Dict:
        if 'fast_ma' in params and 'slow_ma' in params:
             params['slow_ma'] = max(params['slow_ma'], params['fast_ma'])
        return params

    def backtest(self, df: pd.DataFrame, **kwargs) -> Tuple[float, float]:
        fast_ma_param = kwargs.get('fast_ma', self.params['fast_ma']['default'])
        slow_ma_param = kwargs.get('slow_ma', self.params['slow_ma']['default'])

        data = df.copy()
        
        # Calculate moving averages
        data['fast_ma'] = data['close'].rolling(window=fast_ma_param).mean()
        data['slow_ma'] = data['close'].rolling(window=slow_ma_param).mean()
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

