import requests
import logging

logger = logging.getLogger()

class OkxClient:
    def __init__(self, futures=False):
        
        self.futures = futures

        self._base_url = 'https://www.okx.com'

        self.symbols = self._get_symbols()

    def _make_request(self, endpoint: str, query_parameters: dict):
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(self._base_url + endpoint, params=query_parameters, headers=headers, timeout=10)
        except Exception as e:
            logger.error(f'Connection error while making request to {endpoint}: {e}')
            return None
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f'Error while making request to {endpoint}: {response.json()} (status code = {response.status_code})')
            return None

    def _get_symbols(self) -> list[str]:
        
        params = dict()

        params['instType'] = 'SWAP' if self.futures else 'SPOT'

        endpoint = '/api/v5/public/instruments'
        data = self._make_request(endpoint, params)

        symbols = []
        if data and data['code'] == '0':
            symbols = [x['instId'] for x in data['data']]

        return symbols
    
    def get_historical_data(self, symbol: str, start_time: int | None = None, end_time: int | None = None):

        params = dict()

        params['instId'] = symbol
        params['bar'] = '1m'
        params['limit'] = 100

        if start_time is not None:
            params['before'] = start_time
        if end_time is not None:
            params['after'] = end_time

        endpoint = '/api/v5/market/candles'
        raw_candles = self._make_request(endpoint, params)

        candles = []

        if raw_candles is not None and raw_candles['code'] == '0':
            # OKX returns [ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]
            for c in raw_candles['data']:
                candles.append((float(c[0]), float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5]),))
            
            # OKX returns newest first, Binance usually returns oldest first. 
            # To maintain expected behavior (chronological order), we reverse.
            candles.reverse()
            
            return candles
        else:
            return None
