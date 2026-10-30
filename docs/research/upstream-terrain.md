# Upstream terrain — recorded facts

Verified facts about the MLIR fuzzing infrastructure landscape.
Recorded 2026-10-28; re-verify before citing in upstream discussions.
Statements of strategy derived from these facts live in
[docs/requirements.md](../requirements.md).

## OSS-Fuzz: no MLIR coverage

`google/oss-fuzz`, `projects/llvm/build.sh`
(<https://raw.githubusercontent.com/google/oss-fuzz/master/projects/llvm/build.sh>),
retrieved 2026-10-28:

```sh
cmake -GNinja -DCMAKE_BUILD_TYPE=Release ../$LLVM \
    -DLLVM_ENABLE_PROJECTS="clang;lld;clang-tools-extra" \
    -DLLVM_ENABLE_RUNTIMES="libcxx;libcxxabi;compiler-rt" \
```

18 fuzz targets are built — all llvm/clang
(`llvm-opt-fuzzer`, `llvm-isel-fuzzer`, `clang-fuzzer`,
`llvm-dwarfdump-fuzzer`, 5 demangler fuzzers, 2 yaml fuzzers, etc.).
`mlir` is absent from `LLVM_ENABLE_PROJECTS`; no MLIR target is built
or continuously fuzzed.

## llvm-project in-tree: MLIR has two parser fuzzers, no pass-pipeline fuzzer

`mlir/tools/` contains exactly one fuzzer directory,
`mlir/tools/mlir-parser-fuzzer/`, with two entry points:

- `text/mlir-text-parser-fuzzer.cpp`
- `bytecode/mlir-bytecode-parser-fuzzer.cpp`

Both feed raw mutated bytes to the respective parser. No
pass-pipeline fuzzer exists (counterpart: `llvm/tools/llvm-opt-fuzzer/`
on the LLVM side, which OSS-Fuzz additionally runs per-pass:
`llvm-opt-fuzzer--x86_64-instcombine`, `--x86_64-licm`, etc.).

## Related MLIR-fuzzing activity (academic)

- SYNTHFUZZ — "Fuzzing MLIR Compilers with Custom Mutation Synthesis",
  ICSE 2025:
  <https://conf.researchr.org/details/icse-2025/icse-2025-research-track/22/Fuzzing-MLIR-Compilers-with-Custom-Mutation-Synthesis>
- FLEX — "Interleaved Learning and Exploration: A Self-Adaptive Fuzz
  Testing Framework for MLIR" (2025):
  <https://www.researchgate.net/publication/396372878>
  (references MLIRSmith — random MLIR program generation)
- **Ratte** — "Fuzzing for Miscompilations in Multi-Level Compilers
  Using Composable Semantics", ASPLOS 2025, Imperial College London
  (P. Yu et al.):
  <https://www.doc.ic.ac.uk/~afd/papers/2025/ASPLOS-Ratte.pdf>
  — "a framework for specifying composable dialect semantics and
  modular dialect fuzzers"; generation-based (composable per-dialect
  generators) with reference interpreters as the oracle, checking
  semantic preservation across lowering levels; 6 previously-unknown
  miscompilation bugs. Generation-based by design: its oracle needs
  deterministic, well-defined programs (characterized the same way in
  SynthFuzz's related work).
- MLIR-Forge — "Modular IR Fuzzing Engine" (2026-01):
  <https://www.emergentmind.com/topics/mlir-forge>
  — open-source status unverified (open question)
- opencompl/mlir-fuzz — IRDL-based enumerator deriving "fuzzers,
  reducers, or mutators" for MLIR dialects, avoiding non-verifying
  programs: <https://github.com/opencompl/mlir-fuzz>
- **TargetFuzz** — "Targeted Testing of Compiler Optimizations via
  Grammar-Level Composition Styles", Z. Zhou, B. Limpanukorn,
  M. Kim et al., arXiv:2512.04344 (v1 2025-12-04), recorded
  2026-10-29: <https://arxiv.org/abs/2512.04344>
  — grammar-based mutational fuzzer targeting *individual
  optimizations* ("We propose targeted fuzzing of individual
  optimizations to complement pipeline-based testing"); mines
  "composition styles — structural relations over program constructs
  (adjacency, nesting, repetition, ordering) — that optimizations
  look for"; adaptable to MLIR via grammar annotations. Evaluated on
  LLVM and MLIR: +8%/+11% coverage, 2.8×/2.6× optimization-trigger
  rate vs baselines in targeted mode; "it effectively tests all 37
  sampled LLVM optimizations, while pipeline-fuzzing missed 12".
- **MLIRTracer** — "Directed Testing in MLIR: Unleashing Its Potential
  by Overcoming the Limitations of Random Fuzzing", W. Tong, Z. Wang,
  Z. Tang, J. Fang, Y. Zhang, G. Ye, Proc. ACM Softw. Eng.
  2(FSE):2288–2310 (2025), DOI 10.1145/3729372, presented FSE 2025
  (2026-06-24), recorded 2026-10-29:
  <https://dl.acm.org/doi/10.1145/3729372>
  — "a top-down fuzzing approach that targets the highest level of
  MLIR programs (tosa IR) with a directed testing strategy",
  traversing the dialect hierarchy toward lower levels while
  prioritizing bug-prone areas; "MLIRTracer has successfully detected
  73 bugs, with 61 already resolved by the MLIR developers".

## Evidence the fuzzer-found reporting norm is already in use

- llvm/llvm-project issue #233055 (2026-10-17): "[MLIR][TOSA]
  [fuzzer-found] tosa.slice folding returns a tensor with the wrong
  type in tosa-to-tensor" — the `[fuzzer-found]` marking convention
  already appears in MLIR issue titles.
  <https://github.com/llvm/llvm-project/issues/233055>

## Adjacent upstream threads

- [MLIR] Add --list-passes option to mlir-opt (2024-07):
  <https://discourse.llvm.org/t/mlir-add-list-passes-option-to-mlir-opt/80153>
  — landing status unconfirmed; pass enumeration can use the registry
  API regardless.
- Improving testing of crash reproducer generation in MLIR (2025-03):
  <https://discourse.llvm.org/t/improving-testing-of-crash-reproducer-generation-in-mlir/84966>
  — relevant: MLIR pass manager has built-in crash-reproducer support
  with known gaps (multi-threading).
