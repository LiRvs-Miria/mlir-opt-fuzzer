# driver — executable acceptance net for the in-tree target

Out-of-tree verification driver for the acceptance table in
[docs/design/acceptance-criteria.md](docs/design/acceptance-criteria.md):
one probe per acceptance row, run against a **built** `mlir-opt-fuzzer`
binary, PASS/FAIL/RED per row. The net never enters the PR (AC-9) —
it stays in this repository; the PR carries only the target.

## Contract

- `--bin PATH` — the built target binary. Build config: a single
  Release + assertions-off (NDEBUG) build (ruling 2026-11-03).
  Attribution rule: any recorded abort must belong to the target's
  own post-pipeline verify → `abort()` — NDEBUG compiles MLIR asserts
  out, so the judge never mistakes an MLIR assert for a finding.
- Missing / non-executable `--bin` → every row reports **RED** (the
  target is not implemented yet), exit 1. This is the net's starting
  state.
- Probes map onto the acceptance rows; AC-2 carries two input classes
  (it absorbed AC-4). Input-class probes run under a known-good
  pipeline slug — passed as `--pipeline=<slug>` after
  `-ignore_remaining_args=1` (the libFuzzer/CL boundary, FuzzerCLI.h
  `parseFuzzerCLOpts` convention) — because that is the deployment
  state (the target always runs selected); input rejection is a
  property of the input, not of a missing selection:

  | probe | row | verdict is PASS iff |
  |---|---|---|
  | ac2a | AC-2 | `rc == 0`, no artifact |
  | ac2b | AC-2 | `rc == 0`, no artifact |
  | ac3 | AC-3 | `rc == 0`, no artifact |
  | ac5 | AC-5 | `rc == 0`, no artifact |
  | ac6 | AC-6 | `rc == 77` (libFuzzer default `-error_exitcode`, never overridden) **and** exactly one new artifact under the probe's `-artifact_prefix` dir |

  AC-6 runs in **corpus mode** (`-runs=1`, trigger as a one-file
  corpus): libFuzzer records artifacts only in fuzzing/corpus mode —
  in single-file mode the deadly-signal handler deliberately skips
  artifact writing (the input is already on disk).

- Objective signals only: exit code + artifact-file directory diff.
  Output text is captured and discarded, never parsed.
- A raw death (killed by a signal — subprocess reports it as `-n`,
  a shell would say `128+n`, e.g. SIGABRT = -6 / 134) is a **FAIL**
  with an explicit attribution note: the process died without
  libFuzzer recording it, so the abort is not attributable to the
  oracle.
- A driver bug surfaces as `DRIVER BUG:` in the row detail (loud,
  attributable; the table still completes).
- Output: one line per probe + summary; exit 0 iff every probe PASSes,
  else 1.

## Usage

    # RED state (no target yet)
    python3 driver/check.py --bin /nonexistent

    # against a build
    python3 driver/check.py --bin ~/mlir-fuzz-build/bin/mlir-opt-fuzzer

## Not in scope

- Build orchestration — building the tree is a human/CI step; the
  driver consumes a binary path.
- Design-principle rows (AC-1/7/9/10/11) — review-verified, not
  probed (see the acceptance-criteria doc).
- Any campaign logic (corpus management, reporting, stats) — the AC-9
  boundary applies to this repository's tooling too.

## Pins (single points to revisit if the landed PR decides otherwise)

- Pipeline channel: `--pipeline=<slug>` after
  `-ignore_remaining_args=1`, resolved against the target's closed
  vocabulary (`MlirOptFuzzerPipelines.def` in-tree) — slug constants
  in `check.py`. The net and the .def stay in sync: an unknown slug
  fails loud at startup.
- AC-5 slug `cse` (= `builtin.module(func.func(cse))`); AC-6 slug
  `remove-dead-values` (= `builtin.module(remove-dead-values)`).
- libFuzzer `-error_exitcode` default (77).

## Fixtures

- `ac2-garbage.bin` — junk bytes, not MLIR text (AC-2).
- `ac2-pipeline-tail.mlir` — valid module text with a pipeline-looking
  tail; under D-1 the input is module-only, so this is just an
  unparseable module (AC-2, absorbed AC-4).
- `ac3-bytecode.bin` — `ML\xefR` magic + junk; `ML\xefR` is the real
  MLIR bytecode header (BytecodeWriter.cpp emits `"ML\xefR"` as
  "bytecode header").
- `ac5-good.mlir` — minimal valid module (AC-5).
- `ac6-mf007-min-private.mlir` — the **private-form trigger**: derived
  from
  [triage/artifacts/MF-007-min-...mlir](triage/artifacts/MF-007-min-c589551684301db8f78b8aebb0572f9803854169.mlir)
  by a one-token edit (`func.func @data_if` → `func.func private
  @data_if`, serialization per the BUGLOG 2026-10-31 addendum). The
  filed (non-private) artifact is benign under single
  `remove-dead-values` on current main — RDV skips public functions
  (RemoveDeadValues.cpp:278 gate); the private keyword is the trigger
  gate ([BUGLOG](triage/BUGLOG.md) 2026-10-31 / 2026-11-03 addenda).
  This probe rides an **open upstream bug** (semantic layer of
  [#237126](https://github.com/llvm/llvm-project/issues/237126)) —
  re-validate the fixture when it gets fixed.
