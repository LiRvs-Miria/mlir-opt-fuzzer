# prototype — harness framework (framework + incremental development)

The four libFuzzer callbacks live here as skeletons with standard
logging on entry (`llvm::errs()`), filled in incrementally:

- `LLVMFuzzerInitialize` — startup phase (flags, registries, handlers)
- `LLVMFuzzerTestOneInput` — the per-input oracle (D1 lives here)
- `LLVMFuzzerCustomMutator` — structured mutation (spike-report §4-1)
- `LLVMFuzzerCustomCrossOver` — structured splicing

`DummyMlirOptFuzzer.cpp` provides a no-libFuzzer sanity main over
`runFuzzerOnInputs` (DUMMY_MAIN convention, cf.
`mlir/tools/mlir-parser-fuzzer`). The working implementation this
framework was stripped from — driver net, runner scripts, walk record —
is archived in the private reference workspace.

## Build

    cmake -S prototype/harness -B /tmp/proto-build \
          -DMLIR_BUILD_DIR=$HOME/mlir-fuzz-build \
          -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
    cmake --build /tmp/proto-build -j

Two targets: `mlir-opt-fuzzer-proto` (libFuzzer main) and
`mlir-opt-fuzzer-proto-dummy` (plain main, no instrumentation).

## Findings (2026-11-03 walk — design-relevant, keep for the PR)

1. **Anchor no-op footgun.** Raw `parsePassPipeline("builtin.module(X)",
   pm)` with a module-anchored pm nests a *second* module level and
   silently runs nothing — parses fine, executes zero passes. Fix:
   split the flag mlir-opt-style (outer anchor → pm anchor, inner text
   → pipeline). The PR must replicate mlir-opt's anchor semantics.
2. **D-1 × fork-mode tension.** libFuzzer fork mode joins child argv
   unquoted through the shell (`FuzzerCommand.h toString()` →
   `system()`), and pipeline text is full of parentheses. The runner
   embeds shell quotes in the flag value and the harness strips them.
   llvm-opt-fuzzer dodges this whole class via exec-name-encoded
   options — the upstream-grade channel the PR+runner should pick.
3. **Single-file mode writes no artifacts.** In `Running N inputs 1
   time(s)` mode libFuzzer's deadly-signal handler deliberately skips
   artifact writing (the input is already on disk) — exit code only.
   The AC-6 probe therefore runs in corpus mode (`-runs=1`).
4. **Non-reproducing crash artifacts — spike §5 confirmed live.** Fork
   artifacts from clean pipelines replay 0/N single-process: heap
   corruption from an earlier input in the same child kills a later
   one; the artifact records the dying input, not the killer.
   Attribution tool = an ASAN campaign build; until then, triage
   separates reproducing from non-reproducing clusters and only the
   former can become findings (R2 discipline).
