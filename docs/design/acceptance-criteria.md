# In-tree target — design principles and acceptance criteria

Two kinds of promises live here, and the separation is load-bearing
(2026-11-03):

- **Design principles** — how the target is shaped. Verified by
  **review** (the PR diff, the source) — not by running anything.
- **Acceptance criteria** — what the binary does. Verified by **run
  probes**; these are the RED probe list for the implementation.

A row is done when its verification passes. The acceptance probes are
executed by the out-of-tree driver (this repository; the net never
enters the PR). Sources:
[requirements](../requirements/system.md) ·
[thread 84855](https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855) ·
[thread 82556](https://discourse.llvm.org/t/rfc-guidelines-for-fuzzer-generated-issues/82556) ·
[demand-interviews](../research/demand-interviews.md).

D-1: the fuzzer input is only the IR. Which passes run is decided
once at startup, by a command-line flag — the fuzzer never picks or
changes pipelines. Trying a different pipeline means launching the
binary again with a different flag; our out-of-tree runner does that
in bulk (rationale and reopen trigger: [#237126](https://github.com/llvm/llvm-project/issues/237126)).

## Design principles (verified by review)

| id | principle | source | verification |
|----|-----------|--------|--------------|
| AC-1 | The target builds like the parser fuzzers do: `add_llvm_fuzzer`, gated by the tree's fuzzer flags, no bespoke build logic. | R4; `mlir-parser-fuzzer` convention | the tree's own build: compiles under `LLVM_USE_SANITIZE_COVERAGE=ON` |
| AC-7 | Fatal errors inside the pipeline are routed to `abort()` via the installed handler — never a silent exit. | D2 (post 13 bullet 1) | audit: handler installed at init; no `exit()` path bypasses it |
| AC-9 | **No campaign logic in-tree**: no corpus management, no stats/env knobs, no reporting code. | D2; @rengolin post 12; post 13 bullet 1 | audit: PR diff contains only the target + its build wiring |
| AC-10 | The pipeline comes from a command-line flag, checked once at startup (`parsePassPipeline`). A bad flag is a startup error, not something the fuzzer reports. The input never contains pipeline text — that's just an unparseable module (AC-2). | D-1; llvm-opt-fuzzer precedent | audit: no pipeline parsing on the input path; a bad flag errors at startup (one-time check, not a probe) |
| AC-11 | The target has no whitelist/admission logic — it runs whatever pipeline the flag says. Trying out pipelines is the runner's job, out of tree. | D-1; @rengolin post 12 | audit: no whitelist/pairing code in the target source |

## Acceptance criteria (verified by probes — the RED list)

| id | promise | source | probe | status |
|----|---------|--------|-------|--------|
| AC-2 | Input is MLIR module **text**. Unparseable input → return 0: never a crash, never a corpus entry. Pipeline-looking text is the same class — under D-1 the input is module-only, so it can only be an unparseable module. | M1 proposal (post 8); parser-fuzzer convention; absorbs AC-4 | run: garbage bytes → exit 0; module text with a pipeline-looking tail → exit 0 | open |
| AC-3 | Bytecode-magic input → return 0 (text-only target). | parser-fuzzer convention | run: `ML\xefR`-prefixed bytes → exit 0 | open |
| AC-5 | Valid module + valid pipeline + clean run + output verifies → return 0. | D1 | run: known-good module/pipeline pair → exit 0 | open |
| AC-6 | **Post-pipeline verify failure → `abort()`** — libFuzzer records it as a crash artifact. | D1; llvm-opt-fuzzer precedent (`verifyModule` → `abort`) | run: an NDEBUG build fed [MF-007-min](../../triage/artifacts/MF-007-min-c589551684301db8f78b8aebb0572f9803854169.mlir) with `remove-dead-values` ends in a recorded abort — see [BUGLOG](../../triage/BUGLOG.md) 2026-10-31 and 2026-11-03 addenda | open |
| AC-8 | Same input, same outcome — a crash reproduces 10/10 single-process. | spike-report isolation findings | run: crasher ×10 → 10 recorded artifacts | open |

*AC-4 was merged into AC-2 (2026-11-03): under D-1 the input is
module-only, so input text that fails `parsePassPipeline` cannot
exist — pipeline-looking text is just an unparseable module.*

## Boundary

Campaign-side behaviors (corpus admission rates, survival curves,
runner `-keep_seed=1`, positive-control sets) are out-of-tree and are
tested with the campaign tooling — not on this list.
