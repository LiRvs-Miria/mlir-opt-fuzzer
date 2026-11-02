# In-tree target — acceptance criteria (test-first)

Each row is a promise about `mlir/tools/mlir-opt-fuzzer` (the R4/D2
in-tree piece). A row is done when its verification passes; the rows
are the RED probe list for the implementation. Sources trace to the
requirements ([../requirements/system.md](../requirements/system.md))
and to the two upstream threads
([84855](https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855),
[82556](https://discourse.llvm.org/t/rfc-guidelines-for-fuzzer-generated-issues/82556));
verbatim quotes live in
[../research/demand-interviews.md](../research/demand-interviews.md).

Verification kinds: **lit** (a FileCheck test in-tree), **run** (a
libFuzzer invocation with a fixed input and an expected outcome),
**audit** (source inspection, recorded in the PR description).

## Behavioral rows

| id | promise | source | verification | status |
|----|---------|--------|--------------|--------|
| AC-1 | The target builds like the parser fuzzers do: `add_llvm_fuzzer`, gated by the tree's fuzzer flags, no bespoke build logic. | R4; `mlir-parser-fuzzer` convention | lit/build: target compiles under `LLVM_USE_SANITIZE_COVERAGE=ON` | open |
| AC-2 | Input is MLIR module **text**. Unparseable input → return 0: never a crash, never a corpus entry. | M1 proposal (post 8); parser-fuzzer convention | run: garbage bytes → exit 0 | open |
| AC-3 | Bytecode-magic input → return 0 (text-only target; mirrors the parser fuzzers' magic skip). | parser-fuzzer convention | run: `ML\xefR`-prefixed bytes → exit 0 | open |
| AC-4 | Pipeline text that fails `parsePassPipeline` → return 0 (the pipeline-invalid input class is dropped, not reported). | spike-record §3.4 input classes | run: valid module + bogus pipeline → exit 0 | open |
| AC-5 | Valid module + valid pipeline + clean run + output verifies → return 0. | D1 | run: known-good module/pipeline pair → exit 0 | open |
| AC-6 | **Post-pipeline verify failure → `abort()`** — libFuzzer records it as a crash artifact. | D1; llvm-opt-fuzzer precedent (`verifyModule` → `abort`) | run: an NDEBUG build fed [MF-007-min](../../triage/artifacts/MF-007-min-c589551684301db8f78b8aebb0572f9803854169.mlir) with `remove-dead-values` ends in a recorded abort (the pass fails gracefully; only the verifier exposes it — see [BUGLOG](../../triage/BUGLOG.md) 2026-10-31 addendum) | open |
| AC-7 | Fatal errors raised inside the pipeline are routed through an installed fatal-error handler to `abort()` — never a silent exit. | D2 (post 13 bullet 1: "fatal-error handler routed to `abort()` so libFuzzer records it") | audit: handler installed at init; no `exit()` path bypasses it | open |
| AC-8 | Same input, same outcome — deterministic replay (a crash reproduces 10/10 single-process). | spike-report isolation findings | run: crasher ×10 → 10 recorded artifacts | open |
| AC-9 | **No campaign logic in-tree**: no corpus management, no stats/env knobs (e.g. nothing like `MLIR_FUZZ_FIXED_PIPELINE`), no reporting code. The target is the instrument, not the campaign. | D2; @rengolin post 12 (infra out of the monorepo); post 13 bullet 1 | audit: PR diff contains only the target + its build wiring | open |

## Blocked on the open design axis

| id | promise (draft) | blocked by |
|----|-----------------|------------|
| AC-P1 | How the pipeline is selected is decided and testable: encoded in the fuzzed input (mutated jointly with the module) or a fixed per-process flag. | pipeline-selection encoding — the OPEN question (requirements "left to the design phase"; evidence: MF-006/007, [spike-report](../tech-survey/spike-report.md) §3) |
| AC-P2 | Pass admission follows the chosen encoding (whitelist N=3 = 56 passes is the campaign-side default; its in-tree form, if any, depends on AC-P1). | same |

## Boundary

Campaign-side behaviors (corpus admission rates, survival curves,
runner `-keep_seed=1`, positive-control sets) are out-of-tree and are
tested with the campaign tooling — not on this list. The reporting
lane follows C3 and is checked per report, not per commit.
