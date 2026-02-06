import typing
import pandas as pd
import numpy as np

from .base import AbstractStrategy

class IchimokuStrategy(AbstractStrategy):
    def __init__(self):
        super().__init__()
        self.params = {
            'tenkan_period': {'name': 'Tenkan Period', 'type': int, 'default': 9, 'min': 1, 'max': 200},
            'kijun_period': {'name': 'Kijun Period', 'type': int, 'default': 26, 'min': 1, 'max': 200}
        }

    def _donchian(self, high: pd.Series, low: pd.Series, period: int) -> pd.Series:
        """Calculate Donchian Channel midline (used for Ichimoku components)."""
        return (high.rolling(period).max() + low.rolling(period).min()) / 2

    def validate_params(self, params: typing.Dict) -> typing.Dict:
        if 'kijun' in params and 'tenkan' in params:
            pass
        
        params['kijun_period'] = max(params.get('kijun_period', 0), params.get('tenkan_period', 0))
        return params

    def backtest(self, df: pd.DataFrame, **kwargs) -> typing.Tuple[float, float]:
        tenkan_period = kwargs.get('tenkan_period', self.params['tenkan_period']['default'])
        kijun_period = kwargs.get('kijun_period', self.params['kijun_period']['default'])
        
        data = df.copy()
        
        # Ichimoku Components
        data['tenkan_sen'] = self._donchian(data['high'], data['low'], tenkan_period)
        data['kijun_sen'] = self._donchian(data['high'], data['low'], kijun_period)
        data['senkou_span_a'] = ((data['tenkan_sen'] + data['kijun_sen']) / 2).shift(kijun_period)
        data['senkou_span_b'] = self._donchian(data['high'], data['low'], kijun_period * 2).shift(kijun_period)
        data['chikou_span'] = data['close'].shift(kijun_period)
        
        data.dropna(inplace=True)
        
        if len(data) == 0:
            return 0.0, 0.0

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
        
        if len(signals) == 0:
            return 0.0, 0.0
            
        signals['pnl'] = signals['close'].pct_change() * signals['signal'].shift(1)
        signals['cumulative_pnl'] = (1 + signals['pnl']).cumprod()
        signals['max_cumulative_pnl'] = signals['cumulative_pnl'].cummax()
        signals['drawdown'] = (signals['cumulative_pnl'] - signals['max_cumulative_pnl']) / signals['max_cumulative_pnl']
        
        return signals['pnl'].sum(), signals['drawdown'].max()

