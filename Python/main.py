"""Main entry point for crypto backtesting application."""
import logging
from datetime import datetime
from services.data_collector import collect_all
from exchanges.binance import BinanceClient
from exchanges.okx import OkxClient
from backtesting import run

# Logging setup
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler('logs/app.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

EXCHANGES = {'binance': BinanceClient, 'okx': OkxClient}
STRATEGIES = ['obv', 'ichimoku', 'support_resistance', 'sma', 'psar']
TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']


def get_choice(prompt: str, options: list) -> str:
    """Get validated user choice from options."""
    while True:
        choice = input(prompt).lower().strip()
        if choice in options:
            return choice
        logger.warning(f"Invalid choice. Options: {', '.join(options)}")


def get_timestamp(prompt: str, default: int) -> int:
    """Get timestamp from user input."""
    while True:
        date_str = input(prompt).strip()
        if not date_str:
            return default
        try:
            return int(datetime.strptime(date_str, '%Y-%m-%d').timestamp() * 1000)
        except ValueError:
            logger.warning("Invalid date format. Use yyyy-mm-dd")


def main():
    mode = input('Mode (data / backtest / optimize): ').lower().strip()
    exchange = get_choice('Exchange (binance / okx): ', list(EXCHANGES.keys()))
    
    client = EXCHANGES[exchange](futures=True)
    
    while True:
        symbol = input('Symbol: ').upper().strip()
        if symbol in client.symbols:
            break
        logger.warning(f"Symbol {symbol} not found")
    
    if mode == 'data':
        collect_all(client, exchange, symbol)
    
    elif mode == 'backtest':
        strategy = get_choice(f"Strategy ({', '.join(STRATEGIES)}): ", STRATEGIES)
        timeframe = get_choice(f"Timeframe ({', '.join(TIMEFRAMES)}): ", TIMEFRAMES)
        start_time = get_timestamp('Start date (yyyy-mm-dd, empty=all): ', 0)
        end_time = get_timestamp('End date (yyyy-mm-dd, empty=now): ', 
                                  int(datetime.now().timestamp() * 1000))
        
        pnl, drawdown = run(exchange, symbol, strategy, timeframe, start_time, end_time)
        logger.info(f'PnL: {pnl:.2f}% | Max Drawdown: {drawdown:.2f}%')
    
    elif mode == 'optimize':
        logger.info('Optimization not yet implemented')


if __name__ == '__main__':
    main()