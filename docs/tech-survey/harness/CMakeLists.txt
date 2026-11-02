cmake_minimum_required(VERSION 3.20)
project(mlir-spike-harness CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(MLIR REQUIRED CONFIG
  HINTS ${CMAKE_SOURCE_DIR}/../../../mlir-fuzz-build/lib/cmake/mlir
  )

include_directories(${MLIR_INCLUDE_DIRS} ${LLVM_INCLUDE_DIRS})

add_executable(spike-harness spike-harness.cpp)

# Instrumentation at compile, fuzzer runtime (with main) at link only —
# putting -fsanitize=fuzzer in global flags breaks CMake's compiler test.
target_compile_options(spike-harness PRIVATE -fsanitize=fuzzer-no-link)
target_link_options(spike-harness PRIVATE -fsanitize=fuzzer)

target_link_libraries(spike-harness PRIVATE
  MLIRParser
  MLIRPass
  MLIRIR
  MLIRSupport
  MLIRRegisterAllDialects
  MLIRRegisterAllExtensions
  MLIRRegisterAllPasses
  )
