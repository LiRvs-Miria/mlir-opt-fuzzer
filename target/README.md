# target — the in-tree fuzz target

The fuzz target does not live in this repository. The PR carries only
the target and its build wiring (AC-9); campaign and report
infrastructure stays out of the monorepo (R5) — that is what the rest
of this repository hosts. The target's home:

- **In-tree location**: `mlir/tools/mlir-opt-fuzzer/` on
  `llvm/llvm-project` — `mlir-opt-fuzzer.cpp` (the target),
  `DummyOptFuzzer.cpp` (no-libFuzzer sanity main),
  `CMakeLists.txt` (`add_llvm_fuzzer`, modeled on
  `llvm/tools/llvm-opt-fuzzer` and `mlir/tools/mlir-parser-fuzzer`).
- **Development branch**: `mlir-opt-fuzzer` on
  <https://github.com/LiRvs-Miria/llvm-project> — the PR source;
  rebased onto upstream main, never merged locally.

Status: input contract landed (parse as module; empty, bytecode, and
unparseable inputs rejected by returning 0). Pending increments:
startup pass-pipeline selection, post-pipeline output verification
oracle, structured custom mutator.

Verification: the acceptance net in [../driver/](../driver/) runs
against a built target binary:

    python3 driver/check.py --bin <build>/bin/mlir-opt-fuzzer
