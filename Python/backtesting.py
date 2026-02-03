import logging
from services.database import Hdf5Client
from utils import resample_timeframe, STRATEGIES
from strategies.obv import backtest as obv_backtest
from strategies.ichimoku import backtest as ichimoku_backtest
from strategies.support_resistance import backtest as support_resistance_backtest

logger = logging.getLogger()

# Map strategy names to their backtest functions
BACKTEST_FUNCS = {
    'obv': obv_backtest,
    'ichimoku': ichimoku_backtest,
    'support_resistance': support_resistance_backtest,
}


def get_params(strategy: str) -> dict:
    """Prompt user for strategy parameters and return parsed values."""
    strategy_config = STRATEGIES[strategy]
    params = {}
    
    for key, config in strategy_config.items():
        while True:
            user_input = input(f"Enter {config['name']} ({config['default']}): ").strip()
            if user_input == '':
                params[key] = config['default']
                break
            try:
                params[key] = config['type'](user_input)
                break
            except ValueError:
                logger.warning(f"Invalid {config['name']}. Please enter a valid {config['type'].__name__}.")
    
    return params


def run(exchange: str, symbol: str, strategy: str, timeframe: str, start_time: int, end_time: int) -> float:
    """
    Run backtest for a given strategy.
    
    Returns:
        Total PnL percentage
    """
    # Get data
    hdf5_client = Hdf5Client(exchange)
    df = hdf5_client.get_data(symbol, start_time, end_time)
    df = resample_timeframe(df, timeframe)
    
    # Get parameters from user
    params = get_params(strategy)
    
    # Run strategy backtest
    backtest_func = BACKTEST_FUNCS[strategy]
    pnl, drawdown = backtest_func(df, **params)
    
    return pnl, drawdown
