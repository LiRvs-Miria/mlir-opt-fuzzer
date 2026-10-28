# Environment survey — the mlir-opt-fuzzer closed loop

Research frame (vision, user ruling 2026-10-28): establish
`mlir-opt-fuzzer` not as a one-off target but as an automated closed
loop —

```
generate → execute → monitor → reduce → dedupe
```

— stable, low-maintenance, and integrable into CI. The sections below
walk the loop; each records mechanism candidates and the questions this
survey must answer. Nothing is decided here: the closed-loop shape
itself rides on R4 (in-tree target), currently a hypothesis in
[docs/requirements.md](../requirements.md).

## Stage 1 — Generate

- Candidates: seed corpus drawn from `mlir/test` (valid inputs only —
  the valuable-crash class per implementation-boundaries.md); mutation
  strategy (byte-level mutation of `.mlir` text vs structured
  mutation — LLVM's `FuzzMutate`/`IRMutator` is LLVM-IR-specific, so an
  MLIR equivalent would be new upstream work; parser-directed
  dictionaries).
- Questions: what minimum corpus quality makes execution productive?
  does libFuzzer byte mutation suffice for the
  parser→verifier→pipeline oracle chain, or does productivity require
  structured generation? corpus growth and `-merge=1` policy?

## Stage 2 — Execute

- Candidates: the `mlir-opt-fuzzer` target (modeled on
  `llvm-opt-fuzzer` / `FuzzerCLI` conventions): parse input → build a
  pass pipeline → run → verifier; built with sanitizers + assertions.
- Questions: pass-pipeline selection model — fixed per-process variants
  (the OSS-Fuzz `llvm-opt-fuzzer--<pass>` copy pattern) vs in-process
  pipeline selection flags; which dialects/pipelines to cover first;
  determinism and limits (`-timeout`, `-rss_limit_mb`).

## Stage 3 — Monitor

- Candidates: libFuzzer-native crash/assert/hang detection; verifier
  failure surfaced as a distinct signal; a small local runner logging
  campaign state. Upstream surfacing stays manual per the guidelines —
  no auto-filing (the xisang0 thread shows engagement follows triage
  quality, not volume).
- Questions: what does LLVM's own CI run for in-tree fuzz targets today
  (buildbots? sanitizer builds?) and can an MLIR target ride it; where
  does "CI-integrable" realistically attach — building the target in
  LLVM CI, vs an external runner with a public corpus and a stable
  update cadence.

## Stage 4 — Reduce

- Candidates: `mlir-reduce` (`mlir/tools/mlir-reduce` —
  reduction-pattern driven, interestingness-test model); `llvm-reduce`;
  MLIR's built-in pass-manager crash reproducer (generation gaps noted
  in [upstream-terrain.md](upstream-terrain.md)).
- Questions: can `mlir-reduce` consume the fuzzer's crash directly —
  input `.mlir` + pipeline as the interestingness test, minimized
  `.mlir` out — end to end without human glue? what must a reduced
  reproducer contain to satisfy C3 (command line, godbolt-linkable)?

## Stage 5 — Dedupe

- Candidates: canonical-form hashing of reduced reproducers; GitHub
  issue search across open and historical (fixed) issues; corpus dedup
  and issue dedup as two separate passes (per @akorobeynikov).
- Questions: what is the dedupe key — normalized IR text, crash stack
  signature, or root-cause frame? how to check against already-fixed
  bugs across versions (godbolt)?

## Environment baseline (blocking stage 2)

- Local `~/github/llvm-project` checkout state (branch, freshness,
  existing build dirs).
- Cost of an assertions + ASan MLIR build: flags, wall time, disk.
- Whether the in-tree fuzzer targets require any CMake gate to build
  (how `mlir-parser-fuzzer` is enabled today).
