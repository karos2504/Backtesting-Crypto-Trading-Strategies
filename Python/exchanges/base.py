"""Base exchange client with common functionality."""
import logging
import requests
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger()


class BaseExchange(ABC):
    """Abstract base class for exchange clients."""
    
    def __init__(self, base_url: str, futures: bool = False):
        self.base_url = base_url
        self.futures = futures
        self.symbols = self._get_symbols()
    
    def _make_request(self, endpoint: str, params: dict) -> Optional[dict]:
        """Make HTTP GET request with error handling."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(
                self.base_url + endpoint,
                params=params,
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f'Request failed: {endpoint} - {response.status_code}')
        except Exception as e:
            logger.error(f'Connection error: {endpoint} - {e}')
        return None
    
    @abstractmethod
    def _get_symbols(self) -> list[str]:
        """Get available trading symbols."""
        pass
    
    @abstractmethod
    def get_historical_data(self, symbol: str, 
                            start_time: Optional[int] = None,
                            end_time: Optional[int] = None) -> Optional[list]:
        """Fetch historical OHLCV data."""
        pass
