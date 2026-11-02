//===--- spike-harness.cpp — throwaway A1 harness for the spike -----------===//
//
// Input format: first line = pass pipeline spec (unanchored text, e.g.
// "cse,func.func(canonicalize)"); remainder = MLIR module text.
//
// Classification (mutually exclusive, per input):
//   malformed       no newline / empty pipeline or module (input skipped)
//   pipe_invalid    parsePassPipeline failed (pass unknown, dialect missing,
//                   anchor missing) — third input class per the protocol
//   module_invalid  parseSourceString failed (parse/verify rejection)
//   ran             parse+verify ok, pipeline parsed, pm.run completed
//                   (pass-signalled failure still counts as ran)
//
// Env knobs (spike quality, not production):
//   MLIR_FUZZ_FIXED_PIPELINE  use this pipeline for every input, ignoring the
//                             first line — controlled exec/s matrix runs
//   MLIR_FUZZ_STATS           append one per-process summary line at exit:
//                             batch pid=.. execs=.. malformed=.. pipe_invalid=..
//                             module_invalid=.. ran=..
//                             (fork-mode workers exit per batch -> per-batch
//                             lines; single-process -> one final line)
//
// Isolation shape: fresh MLIRContext per input (MLIR fuzzer convention),
// single-threaded, diagnostics swallowed (classification via return values).
//===----------------------------------------------------------------------===//

#include "mlir/IR/BuiltinOps.h"
#include "mlir/IR/Diagnostics.h"
#include "mlir/IR/DialectRegistry.h"
#include "mlir/IR/MLIRContext.h"
#include "mlir/InitAllDialects.h"
#include "mlir/InitAllExtensions.h"
#include "mlir/InitAllPasses.h"
#include "mlir/Parser/Parser.h"
#include "mlir/Pass/PassManager.h"
#include "mlir/Pass/PassRegistry.h"
#include "llvm/ADT/StringRef.h"
#include "llvm/Support/Compiler.h"
#include "llvm/Support/raw_ostream.h"

#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <unistd.h>

using namespace mlir;

namespace {
enum InClass { CL_MALFORMED = 0, CL_PIPE_INVALID, CL_MODULE_INVALID, CL_RAN, CL_MAX };

struct Stats {
  std::atomic<unsigned long> counts[CL_MAX]{};
  unsigned long execs = 0; // per-process; harness is single-threaded
};
Stats g_stats;

void writeStatsAtExit() {
  const char *path = std::getenv("MLIR_FUZZ_STATS");
  if (!path)
    return;
  if (FILE *f = std::fopen(path, "a")) {
    std::fprintf(f,
                 "batch pid=%d execs=%lu malformed=%lu pipe_invalid=%lu "
                 "module_invalid=%lu ran=%lu\n",
                 static_cast<int>(::getpid()), g_stats.execs,
                 g_stats.counts[CL_MALFORMED].load(),
                 g_stats.counts[CL_PIPE_INVALID].load(),
                 g_stats.counts[CL_MODULE_INVALID].load(),
                 g_stats.counts[CL_RAN].load());
    std::fclose(f);
  }
}
struct StatsInstall {
  StatsInstall() { std::atexit(writeStatsAtExit); }
};
StatsInstall g_statsInstall;

std::string g_fixedPipeline;
bool g_haveFixed = false;
} // namespace

// NOTE: must be spelled LLVMFuzzerInitialize — libFuzzer resolves the
// uppercase symbol only; a lowercase llvmFuzzerInitialize is never called
// (silent no-init bug: pass registry stayed empty in the first build).
extern "C" LLVM_ATTRIBUTE_USED int
LLVMFuzzerInitialize(int * /*argc*/, char *** /*argv*/) {
  registerAllPasses();
  if (const char *fp = std::getenv("MLIR_FUZZ_FIXED_PIPELINE")) {
    g_fixedPipeline = fp;
    g_haveFixed = true;
  }
  return 0;
}

extern "C" LLVM_ATTRIBUTE_USED int
LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  if (size == 0)
    return -1;
  g_stats.execs++;
  llvm::StringRef str(reinterpret_cast<const char *>(data), size);

  std::string pipelineText;
  std::string moduleText;
  // Line 1 is always the pipeline spec (also in FIXED_PIPELINE mode, where
  // it is merely ignored — modules must not carry the seed's pipeline line).
  size_t nl = str.find('\n');
  if (nl == llvm::StringRef::npos) {
    g_stats.counts[CL_MALFORMED]++;
    return -1;
  }
  if (g_haveFixed) {
    pipelineText = g_fixedPipeline;
  } else {
    pipelineText = str.substr(0, nl).str();
    while (!pipelineText.empty() &&
           (pipelineText.back() == '\r' || pipelineText.back() == ' '))
      pipelineText.pop_back();
  }
  moduleText = str.substr(nl + 1).str();
  if (pipelineText.empty() || moduleText.empty()) {
    g_stats.counts[CL_MALFORMED]++;
    return -1;
  }

  DialectRegistry registry;
  registerAllDialects(registry);
  // Extensions carry cross-dialect deps (e.g. transform-dialect structured
  // ops) — mlir-opt registers them too; skipping breaks parsing of valid IR.
  registerAllExtensions(registry);
  MLIRContext context(registry);
  context.disableMultithreading();
  // Classification is via return values; keep stderr quiet (hot path).
  context.getDiagEngine().registerHandler([](Diagnostic &) {}); // quiet hot path // quiet hot path

  // Pipeline construction first: cheap string-level rejection gate.
  // (ToT API: running a pipeline requires mlir::PassManager; parsing fills
  // the underlying OpPassManager. Nesting::Implicit mirrors mlir-opt.)
  PassManager pm(&context, ModuleOp::getOperationName(),
                 PassManager::Nesting::Implicit);
  if (failed(parsePassPipeline(pipelineText, pm, llvm::nulls()))) {
    g_stats.counts[CL_PIPE_INVALID]++;
    return 0;
  }

  // Parser requires a null-terminated buffer; std::string guarantees it.
  OwningOpRef<ModuleOp> module =
      parseSourceString<ModuleOp>(moduleText, ParserConfig(&context));
  if (!module) {
    g_stats.counts[CL_MODULE_INVALID]++;
    return 0;
  }

  // Execution. A pass signalling failure is a normal exit, not a crash;
  // genuine crashes (signals, assertions) abort the process and are caught
  // by libFuzzer.
  (void)pm.run(*module);
  g_stats.counts[CL_RAN]++;
  return 0;
}
