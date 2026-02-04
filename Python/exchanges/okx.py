"""OKX exchange client."""
from typing import Optional
from .base import BaseExchange


class OkxClient(BaseExchange):
    """OKX API client."""
    
    def __init__(self, futures: bool = False):
        super().__init__('https://www.okx.com', futures)
    
    def _get_symbols(self) -> list[str]:
        params = {'instType': 'SWAP' if self.futures else 'SPOT'}
        data = self._make_request('/api/v5/public/instruments', params)
        if data and data.get('code') == '0':
            return [x['instId'] for x in data['data']]
        return []
    
    def get_historical_data(self, symbol: str,
                            start_time: Optional[int] = None,
                            end_time: Optional[int] = None) -> Optional[list]:
        params = {'instId': symbol, 'bar': '1m', 'limit': 100}
        if start_time:
            params['before'] = start_time
        if end_time:
            params['after'] = end_time
        
        raw = self._make_request('/api/v5/market/candles', params)
        
        if raw and raw.get('code') == '0':
            candles = [(float(c[0]), float(c[1]), float(c[2]),
                        float(c[3]), float(c[4]), float(c[5])) for c in raw['data']]
            candles.reverse()  # OKX returns newest first
            return candles
        return None
