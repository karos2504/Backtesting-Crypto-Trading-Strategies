"""Binance exchange client."""
from typing import Optional
from .base import BaseExchange

class BinanceClient(BaseExchange):
    """Binance API client."""
    
    def __init__(self, futures: bool = False):
        base_url = 'https://fapi.binance.com' if futures else 'https://api.binance.com'
        super().__init__(base_url, futures)
    
    def _get_symbols(self) -> list[str]:
        endpoint = '/fapi/v1/exchangeInfo' if self.futures else '/api/v3/exchangeInfo'
        data = self._make_request(endpoint, {})
        if data:
            return [x['symbol'] for x in data['symbols']]
        return []
    
    def get_historical_data(self, symbol: str,
                            start_time: Optional[int] = None,
                            end_time: Optional[int] = None) -> Optional[list]:
        params = {'symbol': symbol, 'interval': '1m', 'limit': 1500}
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        
        endpoint = '/fapi/v1/klines' if self.futures else '/api/v3/klines'
        raw = self._make_request(endpoint, params)
        
        if raw:
            return [(float(c[0]), float(c[1]), float(c[2]), 
                     float(c[3]), float(c[4]), float(c[5])) for c in raw]
        return None
