cmake_minimum_required(VERSION 3.20)
project(mlir-opt-fuzzer-proto CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Point at the LLVM build dir at configure time:
#   cmake -S prototype/harness -B /tmp/proto-build \
#     -DMLIR_BUILD_DIR=$HOME/mlir-fuzz-build
set(MLIR_BUILD_DIR "$ENV{HOME}/mlir-fuzz-build" CACHE PATH
  "LLVM/MLIR build directory to link against")

find_package(MLIR REQUIRED CONFIG
  HINTS ${MLIR_BUILD_DIR}/lib/cmake/mlir
  )

include_directories(${MLIR_INCLUDE_DIRS} ${LLVM_INCLUDE_DIRS})

# The fuzzer binary. Instrumentation at compile, fuzzer runtime (with
# main) at link only — putting -fsanitize=fuzzer in global flags breaks
# CMake's compiler test. (Lesson inherited from the spike snapshot.)
add_executable(mlir-opt-fuzzer-proto mlir-opt-fuzzer-proto.cpp)
target_compile_options(mlir-opt-fuzzer-proto PRIVATE -fsanitize=fuzzer-no-link)
target_link_options(mlir-opt-fuzzer-proto PRIVATE -fsanitize=fuzzer)
target_link_libraries(mlir-opt-fuzzer-proto PRIVATE LLVMSupport)

# Sanity-check binary without libFuzzer's main (DUMMY_MAIN convention,
# cf. mlir/tools/mlir-parser-fuzzer): runFuzzerOnInputs loops the file
# arguments. The build-dir libraries carry sanitizer-coverage
# instrumentation, so the dummy links -fsanitize=fuzzer-no-link (no
# libFuzzer main, coverage callbacks only).
add_executable(mlir-opt-fuzzer-proto-dummy
  mlir-opt-fuzzer-proto.cpp
  DummyOptFuzzer.cpp)
target_link_options(mlir-opt-fuzzer-proto-dummy PRIVATE -fsanitize=fuzzer-no-link)
target_link_libraries(mlir-opt-fuzzer-proto-dummy PRIVATE
  LLVMFuzzerCLI
  LLVMSupport
  )
