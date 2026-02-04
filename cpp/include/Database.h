#ifndef DATABASE_H
#define DATABASE_H

#include "Candle.h"
#include <H5Ipublic.h>
#include <string>
#include <vector>

/**
 * HDF5 database client for reading candle data.
 */
class Database {
public:
  Database(const std::string &file_name);
  ~Database();

  std::vector<Candle> get_data(const std::string &symbol,
                               const std::string &exchange);

private:
  hid_t h5_file;

  static int compare_candles(const void *a, const void *b);
};

#endif // DATABASE_H