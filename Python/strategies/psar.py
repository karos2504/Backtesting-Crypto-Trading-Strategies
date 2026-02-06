"""Parabolic SAR Strategy"""
import numpy as np
import pandas as pd
import typing
from typing import Tuple

from .base import AbstractStrategy

class PsarStrategy(AbstractStrategy):
    def __init__(self):
        super().__init__()
        self.params = {
            'initial_af': {'name': 'Initial AF', 'type': float, 'default': 0.02, 'min': 0.01, 'max': 1, 'decimal': 2},
            'max_af': {'name': 'Max AF', 'type': float, 'default': 0.2, 'min': 0.01, 'max': 1, 'decimal': 2},
            'increment': {'name': 'Increment', 'type': float, 'default': 0.02, 'min': 0.01, 'max': 1, 'decimal': 2}
        }

    def validate_params(self, params: typing.Dict) -> typing.Dict:
        # optimize.py constraint:
        # params["initial_acc"] = min(params["initial_acc"], params["max_acc"])
        # params["acc_increment"] = min(params["acc_increment"], params["max_acc"] - params["initial_acc"])
        # Mapping: initial_acc -> initial_af, max_acc -> max_af, acc_increment -> increment
        
        if 'initial_af' in params and 'max_af' in params:
            params['initial_af'] = min(params['initial_af'], params['max_af'])
            
        if 'increment' in params and 'max_af' in params and 'initial_af' in params:
            # Note: params are mutable dicts that have been updated by initial_af split above
            params['increment'] = min(params['increment'], params['max_af'] - params['initial_af'])
            
        return params

    def _calculate_psar(self, high: np.ndarray, low: np.ndarray, close: np.ndarray,
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


    def backtest(self, df: pd.DataFrame, **kwargs) -> Tuple[float, float]:
        initial_af = kwargs.get('initial_af', self.params['initial_af']['default'])
        max_af = kwargs.get('max_af', self.params['max_af']['default'])
        increment = kwargs.get('increment', self.params['increment']['default'])
        
        data = df.copy()
        
        if len(data) < 3:
            return 0.0, 0.0
        
        high = data['high'].values
        low = data['low'].values
        close = data['close'].values
        
        # Calculate PSAR trend
        trend = self._calculate_psar(high, low, close, initial_af, max_af, increment)
        data['signal'] = trend
        
        # Calculate returns
        data['pnl'] = data['close'].pct_change() * data['signal'].shift(1)
        data['cumulative'] = (1 + data['pnl']).cumprod()
        data['max_cumulative'] = data['cumulative'].cummax()
        data['drawdown'] = (data['cumulative'] - data['max_cumulative']) / data['max_cumulative']
        
        total_pnl = data['pnl'].sum() * 100
        max_drawdown = abs(data['drawdown'].min()) * 100
        
        return total_pnl, max_drawdown

