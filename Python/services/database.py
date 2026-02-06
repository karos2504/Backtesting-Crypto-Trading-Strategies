from typing import Tuple, Union
import logging
import h5py
import numpy as np
import pandas as pd
import time
import os
from common.config import DATA_DIR

logger = logging.getLogger()

class Hdf5Client:

    def __init__(self, exchange: str):
        self.exchange = exchange
        self.file = h5py.File(os.path.join(DATA_DIR, f'{exchange}.h5'), 'a')
        self.file.flush()

    def create_dataset(self, symbol: str):
        if symbol not in self.file:
            self.file.create_dataset(symbol, (0, 6), maxshape=(None, 6), dtype='float64')
            self.file.flush()

    def write_data(self, symbol: str, data: list[Tuple]):

        min_time, max_time = self.get_first_last_candle(symbol)

        if min_time is None or max_time is None:
            min_time = float('inf')
            max_time = 0

        filtered_data = []
        
        for d in data:
            if d[0] > max_time:
                filtered_data.append(d)
            elif d[0] < min_time:
                filtered_data.append(d)

        if len(filtered_data) == 0:
            logger.warning(f'No new data found for {symbol}.')
            return

        data_array = np.array(filtered_data)

        self.file[symbol].resize((self.file[symbol].shape[0] + data_array.shape[0]), axis=0)
        self.file[symbol][-data_array.shape[0]:] = data_array
        self.file.flush()

    def get_data(self, symbol: str, from_time: int, to_time: int) -> Union[None, pd.DataFrame]:

        start_query = time.time()

        existing_data = self.file[symbol][:]
        
        if len(existing_data) == 0:
            return None
        
        data = sorted(existing_data, key=lambda x: x[0])
        data = np.array(data)

        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df = df[(df['timestamp'] >= from_time) & (df['timestamp'] <= to_time)]
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.rename(columns={'timestamp': 'date'})
        df = df.set_index('date')

        query_time = round(time.time() - start_query, 2)
        logger.info(f'Retrieved {len(df)} candles for {symbol} from {from_time} to {to_time} in {query_time} seconds.')

        return df

    def get_first_last_candle(self, symbol: str) -> Union[Tuple[None, None], Tuple[float, float]]:
        
        existing_data = self.file[symbol][:]

        if len(existing_data) == 0:
            return None, None
        
        first_candle = min(existing_data, key=lambda x: x[0])[0]
        last_candle = max(existing_data, key=lambda x: x[0])[0]

        return first_candle, last_candle
