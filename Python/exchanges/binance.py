import requests
import logging

logger = logging.getLogger()

class BinanceClient:
    def __init__(self, futures=False):
        
        self.futures = futures

        if self.futures:
            self._base_url = 'https://fapi.binance.com'
        else:    
            self._base_url = 'https://api.binance.com'

        self.symbols = self._get_symbols()

    def _make_request(self, endpoint: str, query_parameters: dict):

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(self._base_url + endpoint, params=query_parameters, headers=headers)
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

        endpoint = '/fapi/v1/exchangeInfo' if self.futures else '/api/v3/exchangeInfo'
        data = self._make_request(endpoint, params)

        symbols = [x['symbol'] for x in data['symbols']]

        return symbols
    
    def get_historical_data(self, symbol: str, start_time: int | None = None, end_time: int | None = None):

        params = dict()

        params['symbol'] = symbol
        params['interval'] = '1m'
        params['limit'] = 1500

        if start_time is not None:
            params['startTime'] = start_time
        if end_time is not None:
            params['endTime'] = end_time

        endpoint = '/fapi/v1/klines' if self.futures else '/api/v3/klines'
        raw_candles = self._make_request(endpoint, params)

        candles = []

        if raw_candles is not None:
            for c in raw_candles:
                candles.append((float(c[0]), float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5]),))
            return candles
        else:
            return None
