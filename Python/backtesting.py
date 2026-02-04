"""Backtesting module for running strategy backtests."""
import logging
from services.database import Hdf5Client
from utils import resample_timeframe, STRATEGIES

# Import strategy backtest functions
from strategies.obv import backtest as obv_backtest
from strategies.ichimoku import backtest as ichimoku_backtest
from strategies.support_resistance import backtest as support_resistance_backtest
from strategies.sma import backtest as sma_backtest
from strategies.psar import backtest as psar_backtest

logger = logging.getLogger()

BACKTEST_FUNCS = {
    'obv': obv_backtest,
    'ichimoku': ichimoku_backtest,
    'support_resistance': support_resistance_backtest,
    'sma': sma_backtest,
    'psar': psar_backtest
}


def get_params(strategy: str) -> dict:
    """Prompt user for strategy parameters."""
    params = {}
    for key, config in STRATEGIES[strategy].items():
        while True:
            user_input = input(f"Enter {config['name']} ({config['default']}): ").strip()
            if not user_input:
                params[key] = config['default']
                break
            try:
                params[key] = config['type'](user_input)
                break
            except ValueError:
                logger.warning(f"Invalid input. Expected {config['type'].__name__}.")
    return params


def run(exchange: str, symbol: str, strategy: str, timeframe: str, 
        start_time: int, end_time: int) -> tuple[float, float]:
    """
    Run backtest for a given strategy.
    
    Returns:
        Tuple of (pnl%, max_drawdown%)
    """
    # Get data
    client = Hdf5Client(exchange)
    df = client.get_data(symbol, start_time, end_time)
    
    if df is None or df.empty:
        logger.error(f"No data found for {symbol}")
        return 0.0, 0.0
    
    df = resample_timeframe(df, timeframe)
    
    # Get parameters and run
    params = get_params(strategy)
    pnl, drawdown = BACKTEST_FUNCS[strategy](df, **params)
    
    return pnl, drawdown
