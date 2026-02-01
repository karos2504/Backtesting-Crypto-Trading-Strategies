from typing import Union
import logging
import time

from exchanges.binance import BinanceClient
from exchanges.okx import OkxClient
from utils import ms_to_datetime
from services.database import Hdf5Client

logger = logging.getLogger()

ONE_MINUTE_MS = 60000

def collect_all(client: Union[BinanceClient, OkxClient], exchange: str, symbol: str) -> None:

    hdf5_client = Hdf5Client(exchange)
    hdf5_client.create_dataset(symbol)

    """
    Collects all available historical kline data for a symbol from the given exchange.
    First fetches the latest data chunk to establish a baseline, then fills forwards (recent)
    and backwards (historical).
    """
    
    # 1. Initial Request
    current_time = int(time.time() * 1000)
    initial_candles = client.get_historical_data(symbol, end_time=current_time)

    if not initial_candles:
        logger.warning(f'No data found for {exchange} {symbol}.')
        return

    if initial_candles[0][0] > initial_candles[-1][0]:
        initial_candles.reverse()

    oldest_db, recent_db = hdf5_client.get_first_last_candle(symbol)
    
    if oldest_db is None or recent_db is None:
        logger.info(f"No existing data for {symbol} in database. Starting fresh.")
        oldest_candle_time = initial_candles[0][0]
        recent_candle_time = initial_candles[-1][0]
    else:
        logger.info(f"Found existing data for {symbol}. Resuming...")
        oldest_candle_time = oldest_db
        recent_candle_time = recent_db

    logger.info(f'Current range: {ms_to_datetime(oldest_candle_time)} to {ms_to_datetime(recent_candle_time)}.')

    # We use a deque or list to store candles for the "History" phase to ensure sorted order on write.
    # Order: [Oldest ... Initial ... Recent]
    all_history_candles = list(initial_candles)

    try:
        # 2. Collect Older Data (Backfill)
        logger.info("Starting backfill (older data)...")
        while True:
            target_end = int(oldest_candle_time - ONE_MINUTE_MS)
            candles = client.get_historical_data(symbol, end_time=target_end)

            if not candles:
                logger.info(f"Backfill complete for {symbol}. No older data returned.")
                break
                
            if candles[0][0] > candles[-1][0]:
                candles.reverse()

            # Deduplicate
            if candles[-1][0] >= oldest_candle_time:
                candles = [c for c in candles if c[0] < oldest_candle_time]
                
            if not candles:
                logger.info("Backfill: No new unique candles found, stopping.")
                break

            oldest_candle_time = candles[0][0]
            
            # Prepend to history
            all_history_candles = candles + all_history_candles
            
            logger.info(f'Backfill found {len(candles)} candles. '
                        f'New oldest: {ms_to_datetime(oldest_candle_time)}.')
            
            time.sleep(0.5)

    except KeyboardInterrupt:
        logger.warning("Backfill interrupted by user. Saving collected data...")
    
    except Exception as e:
        logger.error(f"An error occurred during backfill: {e}")

    # Write all history (Backfill + Initial) to DB once
    if all_history_candles:
        logger.info(f"Writing {len(all_history_candles)} historical candles to database...")
        hdf5_client.write_data(symbol, all_history_candles)
    
    # 3. Collect Recent Data (Forward fill)
    logger.info("Starting forward fill (recent data)...")
    try:
        while True:
            target_start = int(recent_candle_time + ONE_MINUTE_MS)
            candles = client.get_historical_data(symbol, start_time=target_start)

            if not candles:
                break
                
            if candles[0][0] > candles[-1][0]:
                candles.reverse()

            # Deduplicate
            if candles[0][0] <= recent_candle_time:
                candles = [c for c in candles if c[0] > recent_candle_time]
                
            if not candles:
                break

            recent_candle_time = candles[-1][0]
            logger.info(f'Forward fill found {len(candles)} candles. '
                        f'New recent: {ms_to_datetime(recent_candle_time)}.')
            
            # Write directly (Appends)
            hdf5_client.write_data(symbol, candles)
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        logger.warning("Forward fill interrupted by user.")
