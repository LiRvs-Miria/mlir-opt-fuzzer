# Environment survey — build and toolchain

> Renamed from `environment.md` and relocated to the flat sealed
> `research/` (2026-11-02 restructure); the two 2026-10-29
> campaign-era addenda moved to
> [tech-survey/environment.md](../tech-survey/environment.md)
> (each stage keeps its own environment facts).

Researched 2026-10-28 (local machine, Debian 13, LLVM 22 dev checkout at
`~/github/llvm-project`, full clone). Answers below are verified by
building the existing parser fuzzers; the mlir-opt/mlir-reduce subset
was mid-build at freeze (2026-10-28, 1547 steps remaining).
The spike protocol — measurement windows and the number-to-decision
mapping these answers feed — lives in the
[spike-record.md](../tech-survey/spike-record.md) (tech survey;
pre-registered 2026-10-29; re-written 2026-10-30).

## Q1 — Build: minimal MLIR build with `-fsanitize=fuzzer` + assertions

**Working recipe** (validated: both `mlir/tools/mlir-parser-fuzzer`
binaries built and linked with real libFuzzer):

```sh
cmake -G Ninja -B ~/mlir-fuzz-build -S <checkout>/llvm \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLVM_ENABLE_PROJECTS=mlir \
  -DLLVM_TARGETS_TO_BUILD=host \
  -DLLVM_ENABLE_ASSERTIONS=ON \
  -DLLVM_USE_LINKER=lld \
  -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ \
  -DCMAKE_C_FLAGS="-fsanitize=fuzzer-no-link" \
  -DCMAKE_CXX_FLAGS="-fsanitize=fuzzer-no-link" \
  -DLLVM_USE_SANITIZE_COVERAGE=ON \
  -DLLVM_ENABLE_PCH=OFF \
  -DLLVM_INCLUDE_TESTS=OFF -DLLVM_INCLUDE_EXAMPLES=OFF \
  -DLLVM_INCLUDE_DOCS=OFF -DLLVM_ENABLE_BINDINGS=OFF
```

Design: one build directory serves crash oracle (assertions), coverage
(`-fsanitize=fuzzer-no-link` instruments all MLIR/LLVM code), and the
libFuzzer runtime for fuzzer targets. Machine budget: 16 cores / 15 GB
RAM / 266 GB disk; parser-fuzzer subset ≈ 577 steps ≈ 9 min at `-j14`;
`mlir-opt`+`mlir-reduce` subset measured at 1547 steps remaining
(≈ 15–25 min). Configuring took 17 s. Full answers to flags/footprint
confirmed: lld link (installed), no test/example/doc/bindings overhead.

## Q2 — Standalone vs monorepo

Not needed for the spike: the in-tree targets build from the monorepo
directly, and an out-of-tree harness can import the built MLIR via
`MLIR_DIR=~/mlir-fuzz-build/lib/cmake/mlir` (standard standalone-dialect
setup) — deferred until the harness exists.

## Q3 — How `mlir-parser-fuzzer` is wired (in-tree reference)

- `add_llvm_fuzzer()` (llvm/cmake/modules/AddLLVM.cmake) has **three
  modes**: (1) `LLVM_LIB_FUZZING_ENGINE` set → links that engine;
  (2) `LLVM_USE_SANITIZE_COVERAGE=ON` → adds `-fsanitize=fuzzer` to
  CXX flags at target scope; (3) `DUMMY_MAIN` only → plain executable
  that runs input files once each, **no coverage**.
- Pitfalls found by building: passing a flag
  (`LLVM_LIB_FUZZING_ENGINE="-fsanitize=fuzzer"`) is treated as a
  library *path* and breaks the graph — use the libclang_rt fuzzer
  archive path instead
  (`/usr/lib/llvm-22/lib/clang/22/lib/linux/libclang_rt.fuzzer-x86_64.a`).
  `LLVM_USE_SANITIZE_COVERAGE=ON` adds `-fsanitize=fuzzer` at target
  scope, which mismatches the tree-wide PCH built with
  `-fsanitize=fuzzer-no-link`. Also `LLVM_ENABLE_PCH` no longer exists
  in LLVM 22 main (PCH via CMake native `cmake_pch.hxx`, always on) —
  hence the archive-engine recipe above is the PCH-conflict-free form.
- Text fuzzer body: null-terminated input; skips bytecode magic
  (`ML\xefR`); `allowUnregisteredDialects()`; diagnostic handler
  swallows diagnostics (prevents exit-on-error); `parseSourceString`
  discarded.

## Q4 — `llvm-opt-fuzzer` anatomy (template for `mlir-opt-fuzzer`)

- Pass pipeline: `cl::opt --passes`, parse-checked during
  `LLVMFuzzerInitialize` (per-process fixed pipeline); per-pass variants
  via exec-name-encoded options (`llvm-opt-fuzzer--x86_64-licm` copies —
  the OSS-Fuzz pattern seen in build.sh).
- **Custom mutator precedent** (`LLVMFuzzerCustomMutator`):
  parse-and-verify → `IRMutator` (inject/delete/modify instructions) →
  re-verify → write back; mutation outputs that fail verification return
  0 and never enter the corpus. This is the exact LLVM-side precedent
  for an MLIR custom mutator; an MLIR equivalent mutator is
  new work (IRDL-based ideas: opencompl/mlir-fuzz).
- Oracle: verifier-passing input → run pipeline → post-pipeline
  `verifyModule` failure = `abort()` (libFuzzer catches); broken input =
  return 0; fatal errors routed to abort via
  `install_fatal_error_handler`.

## Q5 — Local checkout state

- `~/github/llvm-project`: full clone (6.9 GB), branch
  `tblgen-self-diagnostic` = tblgen diagnostic PR branch merged with
  main as of 2026-10-28 (fresh enough for the spike). Remotes:
  `origin` = fork, `upstream` = llvm/llvm-project. Full `git fetch
  upstream main` times out locally (large delta) — not needed for the
  spike; the merge commit already carries 2026-10-28 main.
- Build directory: `~/mlir-fuzz-build` (outside the repo, ~fresh).


## Addendum 2026-11-04 — add_llvm_fuzzer engine channels: the working config, and a PCH conflict

Machine-verified on this machine while bringing up a second (NDEBUG)
build directory; corrects the Q1 recipe as printed on one point.

- The actually-working campaign build (`~/mlir-fuzz-build`) does not
  run the Q1-printed `LLVM_USE_SANITIZE_COVERAGE=ON`. Its cache has
  `LLVM_LIB_FUZZING_ENGINE=/usr/lib/llvm-22/lib/clang/22/lib/linux/libclang_rt.fuzzer-x86_64.a`
  and `LLVM_USE_SANITIZE_COVERAGE=OFF`: the engine channel links the
  libFuzzer runtime at link time only, while compile-time
  instrumentation comes from the global `-fsanitize=fuzzer-no-link`.
- `LLVM_USE_SANITIZE_COVERAGE=ON` (add_llvm_fuzzer's second branch) is
  **broken on current ToT** for fuzzer targets: the branch injects a
  bare compile-time `-fsanitize=fuzzer` via a directory-scope
  `set(CMAKE_CXX_FLAGS ...)`, and PCH is unconditionally enabled
  (`LLVM_ENABLE_PCH` no longer exists upstream — the configure variable
  is silently ignored as unused). The LLVMSupport PCH is built without
  the fuzzer feature, so every fuzzer target fails to compile —
  "current translation unit is compiled with the target feature
  '-fsanitize=fuzzer' but the precompiled file ... was not" — including
  the upstream `mlir-text-parser-fuzzer` on a fresh NDEBUG build.
  Switching the build to the engine channel fixed it with a 16-step
  incremental rebuild.
- Q1's recipe is superseded on this point: configure with
  `LLVM_LIB_FUZZING_ENGINE=<libclang_rt.fuzzer archive>` and drop
  `LLVM_ENABLE_PCH` (unused).
