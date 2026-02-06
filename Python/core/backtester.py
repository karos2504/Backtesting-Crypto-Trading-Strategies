"""Backtesting module for running strategy backtests."""
import logging
from services.database import Hdf5Client
from common.utils import resample_timeframe

from strategies.obv import ObvStrategy
from strategies.ichimoku import IchimokuStrategy
from strategies.support_resistance import SupResStrategy
from strategies.sma import SmaStrategy
from strategies.psar import PsarStrategy

logger = logging.getLogger()

STRATEGY_MAP = {
    'obv': ObvStrategy,
    'ichimoku': IchimokuStrategy,
    'support_resistance': SupResStrategy,
    'sma': SmaStrategy,
    'psar': PsarStrategy
}

def get_params(strategy_instance) -> dict:
    """Prompt user for strategy parameters."""
    params = {}
    params_info = strategy_instance.params
    
    for key, config in params_info.items():
        while True:
            default_val = config.get('default')
            prompt = f"Enter {config.get('name', key)} ({default_val}): "
            user_input = input(prompt).strip()
            
            if not user_input:
                params[key] = default_val
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
    if strategy not in STRATEGY_MAP:
        logger.error(f"Strategy {strategy} not found")
        return 0.0, 0.0

    # Instantiate strategy
    strategy_instance = STRATEGY_MAP[strategy]()

    # Get data
    client = Hdf5Client(exchange)
    df = client.get_data(symbol, start_time, end_time)
    
    if df is None or df.empty:
        logger.error(f"No data found for {symbol}")
        return 0.0, 0.0
    
    df = resample_timeframe(df, timeframe)
    
    # Get parameters and run
    params = get_params(strategy_instance)
    
    # Validate params (optional but good practice)
    params = strategy_instance.validate_params(params)
    
    pnl, drawdown = strategy_instance.backtest(df, **params)
    
    return pnl, drawdown

