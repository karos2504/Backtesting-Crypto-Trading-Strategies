# Backtesting Crypto Trading Strategies

A backtesting framework for cryptocurrency trading strategies in both C++ and Python.

## Directory Structure

```
.
├── data/                    # Shared data directory
│   └── binance.h5          # HDF5 candle data
├── logs/                    # Shared log files
│   └── app.log
├── cpp/                     # C++ implementation
│   ├── src/                 # Source files
│   ├── include/             # Header files
│   └── CMakeLists.txt      # Build configuration
├── python/                  # Python implementation
│   ├── core/                # Core logic (optimizer, backtester)
│   ├── common/              # Utilities (logger, config)
│   ├── models/              # Data models
│   ├── strategies/          # Trading strategies
│   ├── services/            # Data services
│   ├── exchanges/           # Exchange clients
│   └── main.py             # Entry point
├── .gitignore
└── requirements.txt
```

## Quick Start

### C++
```bash
cd cpp && mkdir build && cd build
cmake .. && make
./backtestingCpp
```

### Python
```bash
python3 python/main.py
```

## Strategies

| Strategy | C++ | Python | Description |
|----------|-----|--------|-------------|
| PSAR | ✅ | ✅ | Parabolic SAR trend following |
| SMA | ✅ | ✅ | Moving average crossover |
| OBV | ❌ | ✅ | On-Balance Volume |
| Ichimoku | ❌ | ✅ | Ichimoku Cloud |
| S/R | ❌ | ✅ | Support/Resistance breakout |
