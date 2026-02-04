#include "strategies/SMA.h"
#include <numeric>

SMA::SMA(const char *exch, const char *sym, const char *interval,
         long long start_ts, long long end_ts) {
  load_data(exch, sym, interval, start_ts, end_ts);
}

void SMA::execute_backtest() { execute_backtest(9, 26); }

void SMA::execute_backtest(int fast_ma, int slow_ma) {
  pnl = 0.0;
  max_drawdown = 0.0;

  if (candles.size() < static_cast<size_t>(slow_ma))
    return;

  double max_pnl = 0.0;
  int position = 0;
  double entry_price = 0.0;

  std::vector<double> fast_window, slow_window;

  for (size_t i = 0; i < candles.size(); i++) {
    fast_window.push_back(candles[i].close);
    slow_window.push_back(candles[i].close);

    if (fast_window.size() > static_cast<size_t>(fast_ma)) {
      fast_window.erase(fast_window.begin());
    }
    if (slow_window.size() > static_cast<size_t>(slow_ma)) {
      slow_window.erase(slow_window.begin());
    }

    if (slow_window.size() < static_cast<size_t>(slow_ma))
      continue;

    double fast_avg =
        std::accumulate(fast_window.begin(), fast_window.end(), 0.0) / fast_ma;
    double slow_avg =
        std::accumulate(slow_window.begin(), slow_window.end(), 0.0) / slow_ma;

    // Long signal
    if (fast_avg > slow_avg && position <= 0) {
      if (position == -1) {
        pnl += (entry_price / candles[i].close - 1) * 100;
        update_drawdown(pnl, max_pnl);
      }
      position = 1;
      entry_price = candles[i].close;
    }
    // Short signal
    else if (fast_avg < slow_avg && position >= 0) {
      if (position == 1) {
        pnl += (candles[i].close / entry_price - 1) * 100;
        update_drawdown(pnl, max_pnl);
      }
      position = -1;
      entry_price = candles[i].close;
    }
  }
}

extern "C" {
SMA *SMA_new(const char *exchange, const char *symbol, const char *interval,
             long long start_ts, long long end_ts) {
  return new SMA(exchange, symbol, interval, start_ts, end_ts);
}

void SMA_execute_backtest(SMA *s, int fast_ma, int slow_ma) {
  s->execute_backtest(fast_ma, slow_ma);
}

double SMA_get_pnl(SMA *s) { return s->get_pnl(); }
double SMA_get_max_drawdown(SMA *s) { return s->get_max_drawdown(); }
}
