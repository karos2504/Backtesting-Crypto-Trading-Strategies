"""Main entry point for crypto backtesting application."""
from datetime import datetime
from services.data_collector import collect_all
from exchanges.binance import BinanceClient
from exchanges.okx import OkxClient
from core.backtester import run
from core.optimizer import Nsga2
from common.config import STRATEGIES, TIMEFRAMES, EXCHANGES
from common.logger import setup_logging

# Logging setup
logger = setup_logging()

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
    exchange = get_choice('Exchange (binance / okx): ', EXCHANGES)
    
    # Map exchange string to Client class
    CLIENT_MAP = {'binance': BinanceClient, 'okx': OkxClient}
    client = CLIENT_MAP[exchange](futures=True)
    
    while True:
        symbol = input('Symbol: ').upper().strip()
        if symbol in client.symbols:
            break
        logger.warning(f"Symbol {symbol} not found")
    
    if mode == 'data':
        collect_all(client, exchange, symbol)
    
    elif mode in ['backtest', 'optimize']:
        strategy = get_choice(f"Strategy ({', '.join(STRATEGIES)}): ", STRATEGIES)
        timeframe = get_choice(f"Timeframe ({', '.join(TIMEFRAMES)}): ", TIMEFRAMES)
        start_time = get_timestamp('Start date (yyyy-mm-dd, empty=all): ', 0)
        end_time = get_timestamp('End date (yyyy-mm-dd, empty=now): ', 
                                  int(datetime.now().timestamp() * 1000))
        if mode == 'backtest':
            pnl, drawdown = run(exchange, symbol, strategy, timeframe, start_time, end_time)
            logger.info(f'PnL: {pnl:.2f}% | Max Drawdown: {drawdown:.2f}%')
            
        elif mode == 'optimize':
            # Population size
            while True:
                try:
                    population_size = int(input('Population size: '))
                    break
                except ValueError:
                    logger.warning("Invalid population size. Use integer")

            # Number of generations
            while True:
                try:
                    generations = int(input('Generations: '))
                    break
                except ValueError:
                    logger.warning("Invalid generations. Use integer")

            # Mutation rate
            while True:
                try:
                    mutation_rate = float(input('Mutation rate: '))
                    break
                except ValueError:
                    logger.warning("Invalid mutation rate. Use float")
            
            nsga2 = Nsga2(exchange, symbol, strategy, timeframe, start_time, end_time, population_size)
            parents = nsga2.run(generations, mutation_rate)
            
            # Print best result
            if parents:
                best_ind = max(parents, key=lambda x: x.pnl)
                print(f"Optimization finished. Best Result: {best_ind}")

if __name__ == '__main__':
    main()