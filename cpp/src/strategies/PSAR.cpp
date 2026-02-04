#include "strategies/PSAR.h"
#include <algorithm>
#include <cmath>

PSAR::PSAR(const char *exch, const char *sym, const char *interval,
           long long start_ts, long long end_ts) {
  load_data(exch, sym, interval, start_ts, end_ts);
}

void PSAR::execute_backtest() { execute_backtest(0.02, 0.2, 0.02); }

void PSAR::execute_backtest(double initial_af, double max_af,
                            double increment) {
  pnl = 0.0;
  max_drawdown = 0.0;

  if (candles.size() < 3)
    return;

  double max_pnl = 0.0;
  int position = 0;
  double entry_price = 0.0;

  double ep[2] = {0, 0};
  double psar[2] = {0, 0};
  double af[2] = {initial_af, initial_af};
  int trend[2] = {0, 0};

  // Initialize
  trend[0] = candles[1].close > candles[0].close ? 1 : -1;
  psar[0] = trend[0] > 0 ? candles[0].high : candles[0].low;
  ep[0] = trend[0] > 0 ? candles[1].high : candles[1].low;

  for (size_t i = 2; i < candles.size(); i++) {
    double temp = psar[0] + af[0] * (ep[0] - psar[0]);

    if (trend[0] < 0) {
      if (trend[0] <= -2) {
        temp =
            std::max(temp, std::max(candles[i - 1].high, candles[i - 2].high));
      }
      trend[1] = temp < candles[i].high ? 1 : trend[0] - 1;
    } else {
      if (trend[0] >= 2) {
        temp = std::min(temp, std::min(candles[i - 1].low, candles[i - 2].low));
      }
      trend[1] = temp > candles[i].low ? -1 : trend[0] + 1;
    }

    ep[1] = trend[1] < 0 ? (trend[1] == -1 ? candles[i].low
                                           : std::min(candles[i].low, ep[0]))
                         : (trend[1] == 1 ? candles[i].high
                                          : std::max(candles[i].high, ep[0]));

    if (std::abs(trend[1]) == 1) {
      psar[1] = ep[0];
      af[1] = initial_af;
    } else {
      psar[1] = temp;
      af[1] = ep[1] == ep[0] ? af[0] : std::min(max_af, af[0] + increment);
    }

    // Long signal
    if (trend[1] == 1 && trend[0] < 0) {
      if (position == -1) {
        pnl += (entry_price / candles[i].close - 1) * 100;
        update_drawdown(pnl, max_pnl);
      }
      position = 1;
      entry_price = candles[i].close;
    }
    // Short signal
    else if (trend[1] < 0 && trend[0] > 0) {
      if (position == 1) {
        pnl += (candles[i].close / entry_price - 1) * 100;
        update_drawdown(pnl, max_pnl);
      }
      position = -1;
      entry_price = candles[i].close;
    }

    trend[0] = trend[1];
    ep[0] = ep[1];
    psar[0] = psar[1];
    af[0] = af[1];
  }
}

extern "C" {
PSAR *PSAR_new(const char *exchange, const char *symbol, const char *interval,
               long long start_ts, long long end_ts) {
  return new PSAR(exchange, symbol, interval, start_ts, end_ts);
}

void PSAR_execute_backtest(PSAR *p, double initial_af, double max_af,
                           double increment) {
  p->execute_backtest(initial_af, max_af, increment);
}

double PSAR_get_pnl(PSAR *p) { return p->get_pnl(); }
double PSAR_get_max_drawdown(PSAR *p) { return p->get_max_drawdown(); }
}