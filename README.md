# Backtesting Crypto Trading Strategies

A backtesting framework for cryptocurrency trading strategies in both C++ and Python.

## Directory Structure

```
.
├── data/                    # Shared data directory
│   └── binance.h5          # HDF5 candle data
├── logs/                    # Shared log files
│   └── app.log
├── C++/                     # C++ implementation
│   ├── strategies/
│   │   ├── Strategy.h      # Base strategy class
│   │   ├── PSAR.h/.cpp     # Parabolic SAR strategy
│   │   └── SMA.h/.cpp      # Moving Average strategy
│   ├── Candle.h            # OHLCV data structure
│   ├── Database.h/.cpp     # HDF5 database client
│   ├── Utils.h/.cpp        # Candle resampling utilities
│   ├── main.cpp            # Entry point
│   └── CMakeLists.txt      # Build configuration
├── Python/                  # Python implementation
│   ├── strategies/
│   │   ├── psar.py         # Parabolic SAR strategy
│   │   ├── sma.py          # Moving Average strategy
│   │   ├── obv.py          # On-Balance Volume strategy
│   │   ├── ichimoku.py     # Ichimoku Cloud strategy
│   │   └── support_resistance.py
│   ├── exchanges/
│   │   ├── base.py         # Base exchange class
│   │   ├── binance.py      # Binance API client
│   │   └── okx.py          # OKX API client
│   ├── services/
│   │   ├── database.py     # HDF5 database client
│   │   └── data_collector.py
│   ├── main.py             # Entry point
│   ├── backtesting.py      # Backtest runner
│   └── utils.py            # Utilities
├── build/                   # C++ build output (gitignored)
└── .gitignore
```

## Quick Start

### C++
```bash
cd build && cmake ../C++ && make
cd ../C++ && ../build/backtestingCpp
```

### Python
```bash
python3 Python/main.py
```

## Strategies

| Strategy | C++ | Python | Description |
|----------|-----|--------|-------------|
| PSAR | ✅ | ✅ | Parabolic SAR trend following |
| SMA | ✅ | ✅ | Moving average crossover |
| OBV | ❌ | ✅ | On-Balance Volume |
| Ichimoku | ❌ | ✅ | Ichimoku Cloud |
| S/R | ❌ | ✅ | Support/Resistance breakout |
