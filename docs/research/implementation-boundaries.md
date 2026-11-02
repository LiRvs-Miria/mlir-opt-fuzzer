# Implementation boundaries — what upstream accepts and rejects

Community norms governing what we file, how, and where. Every boundary
traces to a recorded statement in
[demand-interviews.md](demand-interviews.md). This is research on
community norms, not policy declaration.

## In scope (filed)

| boundary | source |
|---|---|
| crashes/assertions on inputs that pass the verifier (valid IR) | @nikic: "Crashes that occur on valid code are more valuable" |
| crashes in load-bearing conversion passes and core dialects | @kuhar: SPIR-V conversions success recipe; "load-bearing conversion passes... supposed to be resilient to any valid input IR" |
| verifier-internal crashes | @mehdi_amini: "passes should be conservative and resilient against any input IR! I consider this a bug" |
| miscompilations, if a lowering oracle ever exists | @nikic: fuzzer-generated miscompilation reports "very much appreciated", "often analyze and fix within the hour" |

## Out of scope (not filed)

| boundary | source |
|---|---|
| crashes on test-only passes | @kuhar/@mehdi_amini: test passes not resilient by history; signal/noise — collected, not filed |
| crashes on verifier-rejected inputs | @nikic: "fatal errors that do not generate a stack trace should not be reported" |
| missed-optimization reports | @nikic: "we should absolutely decline to fix it as a default policy" |
| fatal errors without stack trace | @nikic: "incorrect use of LLVM, rather than a bug" |

## Report mechanics

| requirement | source |
|---|---|
| marked as fuzzer-generated | @nikic RFC body |
| minimized reproducer + command line + godbolt link, in the issue body | @nikic RFC body |
| deduplicated against own runs and existing issues | @nikic RFC body; @akorobeynikov |
| against ToT `main`, never a release | @nikic RFC body; @akorobeynikov |
| regression window when known (release regression > ancient) | @nikic RFC body |
| title carries root-cause frame, not the low-level assert | @mehdi_amini: "AffineApplyOp canonicalize pattern triggers crash in mlir::simplifyAffineMap()" |
| motivation / practical-use-case argument in the issue body | @banach-space: deprioritising fuzzer-generated issues "unless there's a clear motivation or practical use case" (2026-10, [demand-interviews.md](demand-interviews.md)) |

## Engagement heuristics (observed, not guaranteed)

- Valid-code crashes in load-bearing passes get maintainer engagement;
  artificial-input and test-pass crashes historically do not (xi sang0
  thread).
- Labeling, titling, and dedupe discipline are the currency that
  separates the two outcomes (mehdi_amini's triage post).
- 2026-10 update: maintainer bandwidth pressure made motivation an
  admission criterion — fuzzer-generated issues without a clear
  motivation or practical use case are explicitly deprioritized
  (@banach-space), and fuzzer-generated PRs may be deprioritized in
  crowded areas (@FedericoBruzzone).
