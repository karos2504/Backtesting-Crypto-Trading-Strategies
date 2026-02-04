#include "Database.h"
#include <H5Dpublic.h>
#include <H5Fpublic.h>
#include <H5Ppublic.h>
#include <H5Spublic.h>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <vector>

namespace fs = std::filesystem;

Database::Database(const std::string &file_name) {
  std::string relative_path = "data/" + file_name + ".h5";
  std::vector<std::string> potential_paths = {
      relative_path, "../" + relative_path, "../../" + relative_path};

  std::string path = "";
  for (const auto &p : potential_paths) {
    if (fs::exists(p)) {
      path = p;
      break;
    }
  }

  if (path.empty()) {
    path = relative_path; // Default to original if not found
    printf("Warning: Could not find file in search paths. Trying %s\n",
           path.c_str());
  } else {
    printf("Found data file at: %s\n", path.c_str());
  }

  hid_t fapl = H5Pcreate(H5P_FILE_ACCESS);
  H5Pset_libver_bounds(fapl, H5F_LIBVER_LATEST, H5F_LIBVER_LATEST);
  H5Pset_fclose_degree(fapl, H5F_CLOSE_STRONG);

  printf("Opening %s\n", path.c_str());
  h5_file = H5Fopen(path.c_str(), H5F_ACC_RDONLY, fapl);
  H5Pclose(fapl);

  if (h5_file < 0) {
    printf("Failed to open file %s\n", path.c_str());
    exit(1);
  }
}

Database::~Database() {
  if (h5_file >= 0) {
    H5Fclose(h5_file);
  }
}

std::vector<Candle> Database::get_data(const std::string &symbol,
                                       const std::string &exchange) {
  std::vector<Candle> result;

  hid_t dataset = H5Dopen2(h5_file, symbol.c_str(), H5P_DEFAULT);
  if (dataset < 0) {
    printf("Dataset %s not found\n", symbol.c_str());
    return result;
  }

  auto start = std::chrono::high_resolution_clock::now();

  hid_t dataspace = H5Dget_space(dataset);
  hsize_t dims[2];
  H5Sget_simple_extent_dims(dataspace, dims, nullptr);

  // Read raw data
  std::vector<double> raw(dims[0] * dims[1]);
  H5Dread(dataset, H5T_NATIVE_DOUBLE, H5S_ALL, H5S_ALL, H5P_DEFAULT,
          raw.data());

  // Convert to Candle vector
  result.reserve(dims[0]);
  for (size_t i = 0; i < dims[0]; i++) {
    size_t idx = i * 6;
    result.emplace_back(raw[idx], raw[idx + 1], raw[idx + 2], raw[idx + 3],
                        raw[idx + 4], raw[idx + 5]);
  }

  // Sort by timestamp
  std::qsort(result.data(), result.size(), sizeof(Candle), compare_candles);

  H5Sclose(dataspace);
  H5Dclose(dataset);

  auto end = std::chrono::high_resolution_clock::now();
  auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
  printf("Fetched %zu candles for %s/%s in %lld ms\n", result.size(),
         exchange.c_str(), symbol.c_str(), ms.count());

  return result;
}

int Database::compare_candles(const void *a, const void *b) {
  const Candle *ca = static_cast<const Candle *>(a);
  const Candle *cb = static_cast<const Candle *>(b);
  if (ca->timestamp < cb->timestamp)
    return -1;
  if (ca->timestamp > cb->timestamp)
    return 1;
  return 0;
}
