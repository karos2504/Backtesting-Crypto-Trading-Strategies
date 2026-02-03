from datetime import datetime
import logging
from services.data_collector import collect_all
from exchanges.binance import BinanceClient
from exchanges.okx import OkxClient
from backtesting import run

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('logs/app.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

if __name__ == '__main__':
    mode = input('Choose the program mode (data / backtest/ optimize): ').lower()
    
    while True:
        exchange = input('Choose an exchange: ').lower()
        if exchange in ['binance', 'okx']:
            break
        else:
            logger.warning(f'Exchange {exchange} is not supported.')
    
    if exchange == 'binance':
        client = BinanceClient(True)
    elif exchange == 'okx':
        client = OkxClient(True)
    
    while True:
        symbol = input('Choose a symbol: ').upper()
        if symbol in client.symbols:
            break
        else:
            logger.warning(f'Symbol {symbol} is not supported.')

    if mode == 'data':
        collect_all(client, exchange, symbol)
    elif mode == 'backtest':

        available_strategies = ['obv', 'ichimoku', 'support_resistance']
        available_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']

        # Strategy
        while True:
            strategy = input(f'Choose a strategy ({', '.join(available_strategies)}): ').lower()
            if strategy in available_strategies:
                break
            else:
                logger.warning(f'Strategy {strategy} is not supported.')

        # Timeframe
        while True:
            timeframe = input(f'Choose a timeframe ({', '.join(available_timeframes)}): ').lower()
            if timeframe in available_timeframes:
                break
            else:
                logger.warning(f'Timeframe {timeframe} is not supported.')

        # From
        while True:
            start_time = input('Enter start time (yyyy-mm-dd): ')
            if start_time == "":
                start_time = 0
                break
            try:
                start_time = int(datetime.strptime(start_time, '%Y-%m-%d').timestamp() * 1000)
                break
            except ValueError:
                logger.warning(f'Invalid start time.')

        # To
        while True:
            end_time = input('Enter end time (yyyy-mm-dd): ')
            if end_time == "":
                end_time = int(datetime.now().timestamp() * 1000)
                break
            try:
                end_time = int(datetime.strptime(end_time, '%Y-%m-%d').timestamp() * 1000)
                break
            except ValueError:
                logger.warning(f'Invalid end time.')

        pnl, drawdown = run(exchange, symbol, strategy, timeframe, start_time, end_time)
        logger.info(f'PnL: {pnl:.2f}% | Max Drawdown: {drawdown:.2f}%')
    elif mode == 'optimize':
        pass