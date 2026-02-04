#ifndef UTILS_H
#define UTILS_H

#include "Candle.h"
#include <string>
#include <vector>

/**
 * Resample candles to a given timeframe.
 *
 * @param candles Raw 1-minute candles
 * @param interval Timeframe string (e.g., "5m", "1h", "1d")
 * @param start_ts Start timestamp (ms)
 * @param end_ts End timestamp (ms)
 * @return Resampled candles
 */
std::vector<Candle> resample_candles(const std::vector<Candle> &candles,
                                     const std::string &interval,
                                     long long start_ts, long long end_ts);

#endif // UTILS_H