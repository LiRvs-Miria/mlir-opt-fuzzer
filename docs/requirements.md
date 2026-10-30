# Requirements

The organizing document: all work in this repository derives from
this file, not the other way around. Every requirement traces to a
verbatim source in [`docs/research/`](research/) — quotes, links,
dates. Status meanings:

- `confirmed` — an upstream maintainer voiced the need;
- `hypothesis` — our inference from the recorded context, **pending
  validation**; hypotheses do not become work items until their
  validation signal fires.

## Constraints

| id | constraint | source |
|----|-----------|--------|
| C1 | Public MLIR/LLVM artifacts only (MLIR text/bytecode, LLVM IR, public test corpora); no private-stack inputs anywhere near campaigns or reports | [README](../README.md#scope) scope; author's operating rules (private) |
| C2 | All upstream interaction (discourse, issues, PRs) under a personal identity; GitHub commit email public per LLVM policy (forwarding address acceptable — privacy honored by policy); no LLVM CLA exists — CLA clause superseded, see research addendum 2026-10-30 | [research/demand-research/version-management.md](research/demand-research/version-management.md) (addendum 2026-10-30, was open questions 3–4) |
| C3 | Every report follows the fuzzer-issue mechanics: labeled, ToT base, deduplicated, minimized reproducer + command line + godbolt link, root-cause frame in the title, motivation / practical-use-case argument in the body | [research/demand-research/implementation-boundaries.md](research/demand-research/implementation-boundaries.md), Report mechanics (@banach-space 2026-10 update) |

## Requirements

| id | requirement | source | status | validation signal |
|----|-------------|--------|--------|-------------------|
| R1 | MLIR-specific annex to the fuzzer-generated-issues guidelines (MLIR-adapted wording, no llvm-specific bits) | @kuhar, [guidelines RFC](https://discourse.llvm.org/t/rfc-guidelines-for-fuzzer-generated-issues/82556): "I'd be in favor of adopting the same general guidelines but without some llvm-specific bits" | `confirmed` | annex text reviewed/accepted by MLIR maintainers |
| R2 | Reporting discipline per the guidelines mechanics (C3) | @nikic RFC body; @mehdi_amini triage guidance (root-cause titles) | `confirmed` | filed reports receive engagement/fixes rather than silence |
| R3 | Target class: load-bearing conversion passes and core dialects on valid IR; not test passes | @kuhar SPIR-V success recipe; @mehdi_amini resilience stance | `confirmed` | first confirmed crash filed in this class |
| R4 | An in-tree pass-pipeline fuzzer for MLIR (`mlir-opt-fuzzer`), modeled on `llvm-opt-fuzzer`, landed in `mlir/tools/` | **hypothesis** — inferred from the gap: OSS-Fuzz builds zero MLIR targets; in-tree has two parser fuzzers only ([research/demand-research/upstream-terrain.md](research/demand-research/upstream-terrain.md)). No maintainer has asked for this target | `hypothesis` | maintainer signal in the M1 discourse replies |
| R5 | Continuous campaign infrastructure and eventual OSS-Fuzz integration for MLIR targets | **hypothesis** — follows from R4 | `hypothesis` | deferred until R4 confirms; then re-derived |

## Non-goals (demand-derived)

- **Missed-optimization reports** — @nikic: "we should absolutely
  decline to fix it as a default policy."
- **Test-pass crash reports** — collected locally, not filed
  (@mehdi_amini signal/noise).
- **Novel fuzzing research** — the research lane is crowded
  (SYNTHFUZZ ICSE'25, FLEX, MLIRSmith, MLIR-Forge, TargetFuzz
  arXiv:2512.04344, MLIRTracer FSE'25 —
  [research/demand-research/upstream-terrain.md](research/demand-research/upstream-terrain.md)); this
  project lands infrastructure and reports bugs.
- **Report volume as a goal** — the currency is engagement and fixes,
  per the boundaries in
  [research/demand-research/implementation-boundaries.md](research/demand-research/implementation-boundaries.md).
