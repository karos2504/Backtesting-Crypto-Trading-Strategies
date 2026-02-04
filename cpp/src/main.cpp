#include "strategies/PSAR.h"
#include "strategies/SMA.h"
#include <cstdio>

int main() {
  const char *exchange = "binance";
  const char *symbol = "BTCUSDT";
  const char *interval = "1h";

  long long start_ts = 0LL;
  long long end_ts = 9999999999999LL;

  // PSAR Strategy
  PSAR psar(exchange, symbol, interval, start_ts, end_ts);
  psar.execute_backtest(0.02, 0.2, 0.02);
  printf("PSAR - PnL: %.2f%% | Max Drawdown: %.2f%%\n", psar.get_pnl(),
         psar.get_max_drawdown());

  printf("\n");

  // SMA Strategy
  SMA sma(exchange, symbol, interval, start_ts, end_ts);
  sma.execute_backtest(9, 26);
  printf("SMA - PnL: %.2f%% | Max Drawdown: %.2f%%\n", sma.get_pnl(),
         sma.get_max_drawdown());

  return 0;
}