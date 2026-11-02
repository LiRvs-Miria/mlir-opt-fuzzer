# Requirements

The organizing document: all work in this repository derives from
this file, not the other way around. Every requirement traces to a
verbatim source in [`docs/research/`](../research/) — quotes, links,
dates. Status meanings:

- `confirmed` — an upstream maintainer voiced the need;
- `hypothesis` — our inference from the recorded context, **pending
  validation**; hypotheses do not become work items until their
  validation signal fires.

## Constraints

| id | constraint | source |
|----|-----------|--------|
| C1 | Public MLIR/LLVM artifacts only (MLIR text/bytecode, LLVM IR, public test corpora); no private-stack inputs anywhere near campaigns or reports | [README](../README.md#scope) scope; author's operating rules (private) |
| C2 | All upstream interaction (discourse, issues, PRs) under a personal identity; GitHub commit email public per LLVM policy (forwarding address acceptable — privacy honored by policy); no LLVM CLA exists — CLA clause superseded, see research addendum 2026-10-30 | [research/version-management.md](../research/version-management.md) (addendum 2026-10-30, was open questions 3–4) |
| C3 | Every report follows the fuzzer-issue mechanics: labeled, ToT base, deduplicated, minimized reproducer + command line + godbolt link, root-cause frame in the title, motivation / practical-use-case argument in the body | [research/implementation-boundaries.md](../research/implementation-boundaries.md), Report mechanics (@banach-space 2026-10 update) |

## Requirements

| id | requirement | source | status | validation signal |
|----|-------------|--------|--------|-------------------|
| R1 | MLIR-specific annex to the fuzzer-generated-issues guidelines (MLIR-adapted wording, no llvm-specific bits) | @kuhar, [guidelines RFC](https://discourse.llvm.org/t/rfc-guidelines-for-fuzzer-generated-issues/82556): "I'd be in favor of adopting the same general guidelines but without some llvm-specific bits" | `confirmed` | annex text reviewed/accepted by MLIR maintainers |
| R2 | Reporting discipline per the guidelines mechanics (C3), upgraded to **pattern-level filing**: out-of-tree tooling clusters results by root-cause frame × involved pass, minimizes each distinct pattern with `mlir-reduce`, dedups against open + historical issues, and files **one issue per pattern**, gated on motivation; everything else stays in a local ledger | @nikic RFC body; @mehdi_amini triage guidance (root-cause titles); @rengolin triager-aggregation model — "find common patterns and then only create issues for those common patterns" ([thread post 12](https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855/12)), adopted verbatim in [post 13](https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855/13) with first-hour practice as evidence (#226008 repro commented into the existing issue; #237126 filed as one distinct pattern); noise context making the motivation gate load-bearing: "Current fuzzer issues created in MLIR today are almost entirely solved by people with LLMs 'quick fixing' them a couple of hours later. This is unsustainable." (post 12); verbatim in [research/demand-interviews.md](../research/demand-interviews.md) (2026-10-31 section) | `confirmed` | filed reports receive engagement/fixes rather than silence |
| R3 | Target class: load-bearing conversion passes and core dialects on valid IR; not test passes | @kuhar SPIR-V success recipe; @mehdi_amini resilience stance | `confirmed` | first confirmed crash filed in this class |
| R4 | An in-tree pass-pipeline fuzzer for MLIR (`mlir-opt-fuzzer`), modeled on `llvm-opt-fuzzer`, landed in `mlir/tools/` | @mehdi_amini 2026-10-30, asked directly "is upstream interested in landing such a target in-tree?" ([thread post 8](https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855/8)): "Looks like a good plan to me! Thanks 🙂" ([post 10](https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855/10)); verbatim in [research/demand-interviews.md](../research/demand-interviews.md). Earlier inference from the gap (OSS-Fuzz builds zero MLIR targets; in-tree has two parser fuzzers only — [research/upstream-terrain.md](../research/upstream-terrain.md)) | `confirmed` | in-tree PR lands in `mlir/tools/` following the existing fuzzer-target conventions and is accepted upstream |
| R5 | Campaign / run-and-report infrastructure lives **out of the monorepo**; the future automation home is the buildbot/infra side — engage @infra-area-team when the in-tree target lands. Eventual OSS-Fuzz integration remains the long-term form (notable fact: OSS-Fuzz's llvm project currently builds zero MLIR targets, so no existing auto-filing channel to conflict with) | @rengolin post 12: "If you mean the infra to run and report, then I'd keep it outside of the monorepo. Possibly in the buildbot infra, or some other better place to automate. @infra-area-team may have a better idea what to do here." ([thread post 12](https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855/12)); adopted in [post 13](https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855/13) bullet 3; verbatim in [research/demand-interviews.md](../research/demand-interviews.md) (2026-10-31 section) | `confirmed` (placement); concrete integration form stays open until the infra-area-team discussion | campaigns run out-of-tree with zero conflict against upstream channels; infra-area-team discussion held after the target lands |

## Design inputs (ruled pre-`docs/design/`; the design phase must carry these)

| id | input | basis | date |
|----|-------|-------|------|
| D1 | The target's oracle includes **post-pipeline verification**: a pass that completes but leaves verifier-invalid output is a finding (llvm-opt-fuzzer precedent: `verifyModule` → `abort`) | MF-007 empirical case: on main @ 2026-10-31 the bug is **invisible** to a crash-only oracle (`pm.run` failure counted as `ran`, no crash signal); the only exposure surface is the post-pass verifier — [triage/BUGLOG.md](../../triage/BUGLOG.md) addendum 2026-10-31 | 2026-10-31 |
| D2 | The in-tree piece stays **minimal**: one fuzz target under `mlir/tools/` following the `mlir-parser-fuzzer` conventions — parse → `parsePassPipeline` → run → post-pipeline verify (D1 composes here), with the fatal-error handler routed to `abort()` so libFuzzer records it; **no campaign logic in-tree**; run-and-report infra stays out of the monorepo (R5) | @rengolin post 12 (infra out of monorepo); adopted verbatim in @LiRvs-Miria [post 13](https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855/13) bullets 1/3 — [research/demand-interviews.md](../research/demand-interviews.md) (2026-10-31 section) | 2026-10-31 |

Still open for `docs/design/` (recorded, not ruled): pipeline-selection
encoding (pipeline-in-input vs process-static flags — see
[spike-report.md](../tech-survey/spike-report.md) §3 verdicts).

## Non-goals (demand-derived)

- **Missed-optimization reports** — @nikic: "we should absolutely
  decline to fix it as a default policy."
- **Test-pass crash reports** — collected locally, not filed
  (@mehdi_amini signal/noise).
- **Novel fuzzing research** — the research lane is crowded
  (SYNTHFUZZ ICSE'25, FLEX, MLIRSmith, MLIR-Forge, TargetFuzz
  arXiv:2512.04344, MLIRTracer FSE'25 —
  [research/upstream-terrain.md](../research/upstream-terrain.md)); this
  project lands infrastructure and reports bugs.
- **Report volume as a goal** — the currency is engagement and fixes,
  per the boundaries in
  [research/implementation-boundaries.md](../research/implementation-boundaries.md).
