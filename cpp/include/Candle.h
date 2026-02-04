#ifndef CANDLE_H
#define CANDLE_H

/**
 * Represents a single OHLCV candle.
 */
struct Candle {
  double timestamp;
  double open;
  double high;
  double low;
  double close;
  double volume;

  Candle() : timestamp(0), open(0), high(0), low(0), close(0), volume(0) {}

  Candle(double timestamp, double o, double h, double l, double c, double v)
      : timestamp(timestamp), open(o), high(h), low(l), close(c), volume(v) {}
};

#endif // CANDLE_H
