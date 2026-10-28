# mlir-opt-fuzzer

Upstream fuzzing engineering for MLIR: in-tree fuzz targets, fuzzing
campaigns, and guideline-compliant, root-cause-attributed bug reports.

## Why

MLIR's in-tree fuzzing infrastructure lags the rest of LLVM:

- OSS-Fuzz's `llvm` project builds 18 fuzz targets — **none from MLIR**
  (`mlir` is not even in its `LLVM_ENABLE_PROJECTS`);
- the monorepo carries exactly **two** MLIR fuzz targets (text and
  bytecode parser) and **no pass-pipeline fuzzer** (LLVM core has
  `llvm-opt-fuzzer`);
- meanwhile MLIR's dialect asm parsers, bytecode custom encodings, and
  load-bearing conversion passes form a large, young, under-battered
  robustness surface — and MLIR maintainers have said publicly that they
  want this: SPIR-V conversion fuzzing paid off ("a lot of success"),
  and an MLIR-specific fuzzing guidelines doc has been explicitly asked
  for (discourse, 2025).

## What this repo is

- The engineering home for upstream contributions: an `mlir-opt-fuzzer`
  proposal (modeled on `llvm-opt-fuzzer`), seed corpora drawn from
  `mlir/test`, triage tooling, and a draft MLIR-specific fuzzing
  guidelines document.
- A campaign and bug ledger: every reported issue archived with its
  minimized reproducer, root-cause frame, dedupe notes, and fix
  tracking (see [triage/](triage)).

## What this repo is not

- Not a research fuzzer framework. That space is crowded (SYNTHFUZZ at
  ICSE 2025, FLEX, MLIRSmith, MLIR-Forge); this line lands
  *infrastructure* and reports bugs according to the community's
  fuzzer-issue guidelines, not novel fuzzing research.
- Not tied to any vendor stack: upstream public code only.

## Scope

Consumes public MLIR/LLVM artifacts only: MLIR text/bytecode, LLVM IR,
and public test corpora (`mlir/test`). Requirements and their upstream
sources: [docs/requirements.md](docs/requirements.md); raw research:
[docs/research/](docs/research/).

## Status

Requirements gathering in progress: upstream landscape researched and
demand provenance recorded ([docs/research/](docs/research/)); entering
upstream dialogue. Design starts once requirements stabilize
([docs/requirements.md](docs/requirements.md)).

## Requirements

- Linux with clang; CMake + Ninja
- An `llvm-project` checkout with an MLIR build using
  `-fsanitize=fuzzer` and assertions ON, for campaign runs
- Upstream reduction/dedup tooling from the same monorepo build:
  `mlir-reduce` / `llvm-reduce`

## License

Apache-2.0 WITH LLVM-exception — matching the ecosystem this work
lands in.
