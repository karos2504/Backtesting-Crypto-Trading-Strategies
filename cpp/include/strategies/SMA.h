#ifndef SMA_H
#define SMA_H

#include "Strategy.h"

/**
 * Simple Moving Average crossover strategy.
 */
class SMA : public Strategy {
public:
  SMA(const char *exchange, const char *symbol, const char *interval,
      long long start_ts, long long end_ts);

  void execute_backtest() override;
  void execute_backtest(int fast_ma, int slow_ma);
};

#endif // SMA_H