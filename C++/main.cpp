#include "Database.h"

int main(int, char **) {
  Database db("binance");
  db.get_data("BTCUSDT", "binance");
  db.close_file();
}