#ifndef STRATEGY_H
#define STRATEGY_H

#include "Candle.h"
#include "Database.h"
#include "Utils.h"
#include <string>
#include <vector>

/**
 * Base class for all trading strategies.
 */
class Strategy {
public:
  virtual ~Strategy() = default;
  virtual void execute_backtest() = 0;

  double get_pnl() const { return pnl; }
  double get_max_drawdown() const { return max_drawdown; }

protected:
  std::string exchange;
  std::string symbol;
  std::string timeframe;

  std::vector<Candle> candles;

  double pnl = 0.0;
  double max_drawdown = 0.0;

  // Load and resample candle data
  void load_data(const char *exch, const char *sym, const char *interval,
                 long long start_ts, long long end_ts) {
    exchange = exch;
    symbol = sym;
    timeframe = interval;

    Database db(exch);
    auto raw_candles = db.get_data(sym, exch);
    candles = resample_candles(raw_candles, interval, start_ts, end_ts);
  }

  // Update drawdown tracking
  void update_drawdown(double current_pnl, double &max_pnl) {
    if (current_pnl > max_pnl)
      max_pnl = current_pnl;
    double dd = max_pnl - current_pnl;
    if (dd > max_drawdown)
      max_drawdown = dd;
  }
};

#endif // STRATEGY_H
