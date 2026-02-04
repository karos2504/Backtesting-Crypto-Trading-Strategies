#include "Utils.h"
#include <cmath>
#include <cstdio>

namespace {
double parse_timeframe_ms(const std::string &interval) {
  size_t pos;
  if ((pos = interval.find('m')) != std::string::npos) {
    return std::stoi(interval.substr(0, pos)) * 60 * 1000.0;
  } else if ((pos = interval.find('h')) != std::string::npos) {
    return std::stoi(interval.substr(0, pos)) * 60 * 60 * 1000.0;
  } else if ((pos = interval.find('d')) != std::string::npos) {
    return std::stoi(interval.substr(0, pos)) * 24 * 60 * 60 * 1000.0;
  }
  printf("Invalid timeframe: %s\n", interval.c_str());
  return 0;
}
} // namespace

std::vector<Candle> resample_candles(const std::vector<Candle> &candles,
                                     const std::string &interval,
                                     long long start_ts, long long end_ts) {
  std::vector<Candle> result;

  if (candles.empty())
    return result;

  double tf_ms = parse_timeframe_ms(interval);
  if (tf_ms <= 0)
    return result;

  Candle current;
  bool has_current = false;

  for (const auto &c : candles) {
    if (c.timestamp < start_ts)
      continue;
    if (c.timestamp > end_ts)
      break;

    double bucket_ts = c.timestamp - std::fmod(c.timestamp, tf_ms);

    if (!has_current) {
      current = {bucket_ts, c.open, c.high, c.low, c.close, c.volume};
      has_current = true;
      continue;
    }

    if (c.timestamp >= current.timestamp + tf_ms) {
      result.push_back(current);
      current = {bucket_ts, c.open, c.high, c.low, c.close, c.volume};
    } else {
      if (c.high > current.high)
        current.high = c.high;
      if (c.low < current.low)
        current.low = c.low;
      current.close = c.close;
      current.volume += c.volume;
    }
  }

  if (has_current) {
    result.push_back(current);
  }

  printf("Resampled to %zu candles for timeframe %s\n", result.size(),
         interval.c_str());
  return result;
}