# 2026-10-28 — Upstream landscape recon (M0 provenance archive)

Sources-first record of the recon that shaped this project's strategy.
Every claim below links its source. Append-only: later findings get new
dated sections, history stays intact.

## Etiquette and channels

- **[RFC] Guidelines for fuzzer-generated issues** (nikic, 2024-10,
  broad support):
  <https://discourse.llvm.org/t/rfc-guidelines-for-fuzzer-generated-issues/82556>
  — label issues as fuzzer-generated; minimized reproducer + command
  line + godbolt link; dedupe against prior reports; report against
  ToT; note regression window when known. Crashes on valid code are
  the valuable kind; crashes on syntactically-valid-but-unrealistic IR
  need plausibility triage. Missed-optimization reports need
  real-world relevance — we do not do those.
- **MLIR maintainer demand**: kuhar in the RFC thread — "From the MLIR
  POV, I'd be in favor of adopting the same general guidelines but
  without some llvm-specific bits" = an MLIR-specific guidelines
  annex is an explicitly requested contribution (our M4).

## The prior conversation (our exact idea, already discussed)

- **Fuzzing MLIR Infrastructure** (xisang0, 2025-02;
  mehdi_amini + kuhar replying):
  <https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855>
  - Failure modes observed: crashes on artificial inputs and on test
    passes get no engagement; titles naming the low-level assert
    (`Casting.h:656`) instead of the root-cause frame are hard to
    triage.
  - Success recipe (kuhar): fuzzing the **SPIR-V dialect and related
    conversions** — "a lot of success... relatively simple oversights
    in our test coverage that the fuzzer helped close."
  - mehdi_amini: passes *should* be resilient to any input IR (not
    doing so "is a bug"), but today test passes are not — hence the
    signal/noise problem. Triage guidance: title should name
    `Pass pattern triggers crash in <actual function>`.
  - xisang0's filed issues:
    <https://github.com/llvm/llvm-project/issues?q=is%3Aissue%20state%3Aopen%20author%3Axisang0>

## Infrastructure gap (verified 2026-10-28)

- OSS-Fuzz `projects/llvm/build.sh`
  (<https://raw.githubusercontent.com/google/oss-fuzz/master/projects/llvm/build.sh>):
  18 fuzz targets, all llvm/clang; `-DLLVM_ENABLE_PROJECTS="clang;lld;clang-tools-extra"`
  — **MLIR is not even built**. No continuous public fuzzing of MLIR
  exists.
- In-tree MLIR fuzz targets: exactly two, both parser-level
  (`mlir/tools/mlir-parser-fuzzer/{text,bytecode}`), byte-diff mutation
  only. No pass-pipeline fuzzer (`llvm-opt-fuzzer` has no MLIR
  counterpart).
- mlir-opt `--list-passes`: RFC'd 2024-07
  (<https://discourse.llvm.org/t/mlir-add-list-passes-option-to-mlir-opt/80153>),
  not confirmed landed — pass enumeration will use the registry API
  regardless.

## Academic prior art (research lane is closed; engineering lane unaffected)

- SYNTHFUZZ — "Fuzzing MLIR Compilers with Custom Mutation Synthesis",
  ICSE 2025:
  <https://conf.researchr.org/details/icse-2025/icse-2025-research-track/22/Fuzzing-MLIR-Compilers-with-Custom-Mutation-Synthesis>
- FLEX — "Interleaved Learning and Exploration: A Self-Adaptive Fuzz
  Testing Framework for MLIR" (2025):
  <https://www.researchgate.net/publication/396372878>
- MLIRSmith — random MLIR program generation (referenced from FLEX).
- MLIR-Forge — "Modular IR Fuzzing Engine" (2026-01,
  <https://www.emergentmind.com/topics/mlir-forge>) — open-source
  status unverified (roadmap open question).

## Rulings recorded this day

- Bandwidth (user): MLIR engineering track promoted to primary,
  ptrfuzz demoted to secondary; rationale — upstream fuzzing work
  feeds compiler and fuzzing fundamentals first (career-plan §4.7,
  2026-10-28).
- Differentiation vs xisang0 (not "first", but "institutional"):
  in-tree infrastructure that outlives a campaign, conversion-pass
  targeting, and triage discipline per the guidelines — vs a stream of
  untriaged crash reports.
- Language ruling (user): this repository is English-only — it faces
  the global upstream community.
