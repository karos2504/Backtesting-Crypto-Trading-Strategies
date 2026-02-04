#ifndef PSAR_H
#define PSAR_H

#include "Strategy.h"

/**
 * Parabolic SAR trading strategy.
 */
class PSAR : public Strategy {
public:
  PSAR(const char *exchange, const char *symbol, const char *interval,
       long long start_ts, long long end_ts);

  void execute_backtest() override;
  void execute_backtest(double initial_af, double max_af, double increment);
};

#endif // PSAR_H