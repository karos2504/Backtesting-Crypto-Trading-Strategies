cmake_minimum_required(VERSION 3.10)
project(backtestingCpp VERSION 0.1.0)
set(CMAKE_CXX_STANDARD 17)

include(CTest)
enable_testing()
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(HDF5 REQUIRED COMPONENTS C)

include_directories(${HDF5_INCLUDE_DIRS} include .)

set(SOURCE_FILES src/main.cpp src/Database.cpp src/Utils.cpp src/strategies/SMA.cpp src/strategies/PSAR.cpp)

add_executable(${PROJECT_NAME} ${SOURCE_FILES})

target_link_libraries(${PROJECT_NAME} ${HDF5_LIBRARIES} ${HDF5_C_LIBRARIES})

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
