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

#include "mlir/IR/BuiltinOps.h"
#include "mlir/IR/Diagnostics.h"
#include "mlir/IR/MLIRContext.h"
#include "mlir/InitAllDialects.h"
#include "mlir/InitAllExtensions.h"
#include "mlir/Parser/Parser.h"
#include "llvm/ADT/StringRef.h"
#include "llvm/Support/Compiler.h"

using namespace mlir;


extern "C" LLVM_ATTRIBUTE_USED int LLVMFuzzerInitialize(int *argc, 
                                                        char ***argv) {
  return 0;
}

extern "C" LLVM_ATTRIBUTE_USED int LLVMFuzzerTestOneInput(const uint8_t *data, 
                                                          size_t size) {
  // Skip empty inputs.
  if (size == 0)
    return 0;
  llvm::StringRef str(reinterpret_cast<const char *>(data), size);
  // Skip if bytecode.
  if (str.starts_with("ML\xefR"))
    return 0;

  DialectRegistry registry;
  registerAllDialects(registry);
  registerAllExtensions(registry);
  MLIRContext context(registry);
  // Sequential pass execution for deterministic replay; also skips
  // context locking, useless in a single-threaded exec.
  context.disableMultithreading();
  // Register diagnostic handler to avoid triggering exit behavior.
  context.getDiagEngine().registerHandler(
      [](mlir::Diagnostic &diag) { return; });

  OwningOpRef<ModuleOp> module =
      parseSourceString<ModuleOp>(str, ParserConfig(&context));
  if (!module)
    return 0;

  return 0;
}

extern "C" LLVM_ATTRIBUTE_USED size_t LLVMFuzzerCustomMutator(uint8_t *Data, size_t Size, 
                                                              size_t MaxSize, unsigned Seed) {
  return 0;
}

extern "C" LLVM_ATTRIBUTE_USED size_t LLVMFuzzerCustomCrossOver(const uint8_t *Data1, size_t Size1,
                                                                const uint8_t *Data2, size_t Size2, uint8_t *Out,
                                                                size_t MaxOutSize, unsigned Seed) {
  return 0;
}
