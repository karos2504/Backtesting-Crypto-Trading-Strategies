import numpy as np
import pandas as pd
from typing import Tuple

def backtest(df: pd.DataFrame, min_points: int, min_diff_points: int, 
             rounding_nb: float, take_profit: float, stop_loss: float) -> Tuple[float, float]:
    """
    Backtest Support/Resistance breakout strategy.
    
    Returns:
        Tuple of (total_pnl, max_drawdown)
    """
    candle_length = df.iloc[1].name - df.iloc[0].name
    
    # State
    pnl_list = []
    trade_side = 0
    entry_price = None
    
    # Round prices for level detection
    df = df.copy()
    df['rounded_high'] = (df['high'] / rounding_nb).round() * rounding_nb
    df['rounded_low'] = (df['low'] / rounding_nb).round() * rounding_nb
    
    # Convert to numpy for performance
    highs = df['high'].values
    lows = df['low'].values
    rounded_highs = df['rounded_high'].values
    rounded_lows = df['rounded_low'].values
    closes = df['close'].values
    times = df.index.values
    
    price_groups = {'supports': {}, 'resistances': {}}
    levels = {'supports': [], 'resistances': []}
    last_hl = {'supports': [], 'resistances': []}
    
    for i in range(len(highs)):
        ts = times[i]
        
        for side in ['resistances', 'supports']:
            is_res = (side == 'resistances')
            price = highs[i] if is_res else lows[i]
            rounded = rounded_highs[i] if is_res else rounded_lows[i]
            close = closes[i]
            
            # Count breaks in recent history
            breaks = sum(1 for p in last_hl[side] if (p > price if is_res else p < price))
            
            # Update or create price group
            if rounded in price_groups[side]:
                grp = price_groups[side][rounded]
                
                if grp['start_time'] is None and breaks < 3:
                    grp['start_time'] = ts
                
                if breaks < 3 and (grp['last'] is None or ts >= grp['last'] + min_diff_points * candle_length):
                    grp['prices'].append(price)
                    grp['last'] = ts
                    
                    if len(grp['prices']) >= min_points:
                        extreme = max(grp['prices']) if is_res else min(grp['prices'])
                        levels[side].append({'price': extreme, 'broken': False})
            else:
                if breaks < 3:
                    price_groups[side][rounded] = {'prices': [price], 'start_time': ts, 'last': ts}
            
            # Invalidate broken groups
            for grp in price_groups[side].values():
                if grp['prices']:
                    extreme = max(grp['prices']) if is_res else min(grp['prices'])
                    if (is_res and price > extreme) or (not is_res and price < extreme):
                        grp['prices'] = []
                        grp['start_time'] = None
                        grp['last'] = None
            
            # Update history (keep last 10)
            last_hl[side].append(price)
            if len(last_hl[side]) > 10:
                last_hl[side].pop(0)
            
            # Check for breakout entry
            for level in levels[side]:
                if not level['broken']:
                    breakout = close > level['price'] if is_res else close < level['price']
                    if breakout:
                        level['broken'] = True
                        if trade_side == 0:
                            entry_price = close
                            trade_side = 1 if is_res else -1
            
            # Check TP/SL
            if trade_side != 0 and entry_price:
                tp_pct = take_profit / 100
                sl_pct = stop_loss / 100
                
                if trade_side == 1:
                    hit_tp = close >= entry_price * (1 + tp_pct)
                    hit_sl = close <= entry_price * (1 - sl_pct)
                    if hit_tp or hit_sl:
                        pnl_list.append((close / entry_price - 1) * 100)
                        trade_side = 0
                        entry_price = None
                elif trade_side == -1:
                    hit_tp = close <= entry_price * (1 - tp_pct)
                    hit_sl = close >= entry_price * (1 + sl_pct)
                    if hit_tp or hit_sl:
                        pnl_list.append((entry_price / close - 1) * 100)
                        trade_side = 0
                        entry_price = None
    
    # Calculate drawdown
    if pnl_list:
        cumulative = np.cumprod(1 + np.array(pnl_list) / 100)
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = (cumulative - running_max) / running_max
        max_drawdown = drawdowns.min()
    else:
        max_drawdown = 0.0
    
    return sum(pnl_list), max_drawdown
