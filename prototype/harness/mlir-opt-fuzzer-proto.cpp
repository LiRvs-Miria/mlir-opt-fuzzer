//===--- mlir-opt-fuzzer-proto.cpp - Prototype of the MLIR opt fuzzer -===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//
//
// Out-of-tree framework for the in-tree target (R4): the four libFuzzer
// callbacks, filled in incrementally. The working implementation this
// framework was stripped from is archived in the private reference
// workspace (reference/prototype/).
//
//===----------------------------------------------------------------------===//

#include "llvm/Support/raw_ostream.h"


extern "C" LLVM_ATTRIBUTE_USED int LLVMFuzzerInitialize(int *argc, 
                                                        char ***argv) {
  llvm::errs() << "mlir-opt-fuzzer-proto: LLVMFuzzerInitialize\n";
  return 0;
}

extern "C" LLVM_ATTRIBUTE_USED int LLVMFuzzerTestOneInput(const uint8_t *data, 
                                                          size_t size) {
  llvm::errs() << "mlir-opt-fuzzer-proto: LLVMFuzzerTestOneInput\n";
  return 0;
}

extern "C" LLVM_ATTRIBUTE_USED size_t LLVMFuzzerCustomMutator(uint8_t *Data, size_t Size, 
                                                              size_t MaxSize, unsigned Seed) {
  llvm::errs() << "mlir-opt-fuzzer-proto: LLVMFuzzerCustomMutator\n";
  return 0;
}

extern "C" LLVM_ATTRIBUTE_USED size_t LLVMFuzzerCustomCrossOver(const uint8_t *Data1, size_t Size1,
                                                                const uint8_t *Data2, size_t Size2, uint8_t *Out,
                                                                size_t MaxOutSize, unsigned Seed) {
  llvm::errs() << "mlir-opt-fuzzer-proto: LLVMFuzzerCustomCrossOver\n";
  return 0;
}
