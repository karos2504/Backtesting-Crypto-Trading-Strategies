#include "Database.h"
#include <H5Fpublic.h>
#include <H5Ipublic.h>
#include <H5Ppublic.h>
#include <H5public.h>
#include <chrono>
#include <cstddef>
#include <cstdlib>
#include <string>

using namespace std;

Database::Database(const string &file_name) {
  string FILE_NAME = "data/" + file_name + ".h5";
  hid_t fapl = H5Pcreate(H5P_FILE_ACCESS);

  herr_t status =
      H5Pset_libver_bounds(fapl, H5F_LIBVER_LATEST, H5F_LIBVER_LATEST);
  status = H5Pset_fclose_degree(fapl, H5F_CLOSE_STRONG);

  printf("Opening %s\n", FILE_NAME.c_str());
  h5_file = H5Fopen(FILE_NAME.c_str(), H5F_ACC_RDONLY, fapl);

  if (h5_file < 0) {
    printf("Failed to open file %s", FILE_NAME.c_str());
    exit(1);
  }
}

void Database::close_file() { H5Fclose(h5_file); }

double **Database::get_data(const string &symbol, const string &exchange) {
  double **result = {};

  hid_t dataset = H5Dopen2(h5_file, symbol.c_str(), H5P_DEFAULT);

  if (dataset == -1) {
    return result;
  }

  auto start_ts = chrono::high_resolution_clock::now();

  hid_t dataspace = H5Dget_space(dataset);
  hsize_t dims[2];

  H5Sget_simple_extent_dims(dataspace, dims, NULL);

  result = new double *[dims[0]];

  for (size_t i = 0; i < dims[0]; i++) {
    result[i] = new double[dims[1]];
  }

  double *candle_data = new double[dims[0] * dims[1]];

  H5Dread(dataset, H5T_NATIVE_DOUBLE, H5S_ALL, H5S_ALL, H5P_DEFAULT,
          candle_data);

  int j = 0;

  for (int i = 0; i < dims[0] * dims[1]; i += 6) {
    result[j][0] = candle_data[i];
    result[j][1] = candle_data[i + 1];
    result[j][2] = candle_data[i + 2];
    result[j][3] = candle_data[i + 3];
    result[j][4] = candle_data[i + 4];
    result[j][5] = candle_data[i + 5];
    j++;
  }

  delete[] candle_data;

  qsort(result, dims[0], sizeof(result[0]), compare);

  H5Sclose(dataspace);
  H5Dclose(dataset);

  auto end_ts = chrono::high_resolution_clock::now();
  auto duration =
      chrono::duration_cast<chrono::milliseconds>(end_ts - start_ts);
  printf("Fetched %i candles for %s/%s in %i ms\n", (int)dims[0],
         exchange.c_str(), symbol.c_str(), (int)duration.count());

  return result;
}

int compare(const void *a, const void *b) {
  const double *a_ptr = *(const double **)a;
  const double *b_ptr = *(const double **)b;

  if (a_ptr[0] == b_ptr[0]) {
    return 0;
  } else if (a_ptr[0] < b_ptr[0]) {
    return -1;
  } else {
    return 1;
  }
}
