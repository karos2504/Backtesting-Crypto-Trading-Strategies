#include <H5Ipublic.h>
#include <string>

class Database {
public:
  Database(const std::string &file_name);
  void close_file();
  double **get_data(const std::string &symbol, const std::string &exchange);

  hid_t h5_file;
};

int compare(const void *a, const void *b);