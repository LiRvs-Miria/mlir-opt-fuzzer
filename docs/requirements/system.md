# Requirements — what we build, and the rules we hold

This file is the source of truth for the project's scope: nothing in
this repository happens that doesn't trace back to a line here, and
every line here traces to something a maintainer actually said —
quotes and links live in [research/](../research/).

The project in one sentence: **bring fuzzing to MLIR the way this
community wants it** — one fuzz target in-tree, campaigns out of tree,
and bug reports maintainers actually want to read.

Status of each line below: `confirmed` = a maintainer said it.
`hypothesis` = we believe it, and we wait for a signal before acting
on it.

## Constraints (rules we don't break)

| id | rule | source |
|----|------|--------|
| C1 | Public MLIR/LLVM artifacts only — MLIR text/bytecode, LLVM IR, public test corpora. Campaigns and reports never touch private-stack inputs. | README scope; author's operating rules (private) |
| C2 | All upstream interaction under a personal identity; commit email public per LLVM policy (a forwarding address is fine — the policy itself honors privacy). LLVM has no CLA. | [version-management.md](../research/version-management.md) (addendum 2026-10-30) |
| C3 | Every report follows the fuzzer-issue mechanics: label it fuzzer-generated, verify against current `main`, deduplicate, attach a minimized reproducer + command line + godbolt link, put the root-cause frame in the title, and make the motivation case in the body. | [implementation-boundaries.md](../research/implementation-boundaries.md), Report mechanics (@banach-space 2026-10 update) |

## Requirements (what we're building)

| id | requirement | source | status | done when |
|----|-------------|--------|--------|-----------|
| R1 | An MLIR-specific annex to the fuzzer-issue guidelines — the same general rules, minus the llvm-specific bits (optimization levels, fast math, …). | @kuhar, guidelines RFC: "I'd be in favor of adopting the same general guidelines but without some llvm-specific bits" | `confirmed` | maintainers accept the annex text |
| R2 | Never file raw crashes. Cluster crashes locally by root cause, minimize one reproducer per pattern (`mlir-reduce`), check open and historical issues, file at most one issue per pattern — and only when we can argue why it matters. Everything else stays in the local ledger. | @rengolin post 12: "find common patterns and then only create issues for those common patterns"; adopted in post 13; the noise problem that makes the motivation gate load-bearing (post 12): "…almost entirely solved by people with LLMs 'quick fixing' them a couple of hours later. This is unsustainable."; verbatim in [demand-interviews.md](../research/demand-interviews.md) (2026-10-31 section) | `confirmed` | filed issues get engagement and fixes, not silence |
| R3 | Point the fuzzer at load-bearing conversion passes and core dialects running on valid IR — not at test passes. That is where maintainer engagement lives. | @kuhar (SPIR-V success recipe); @mehdi_amini (resilience stance) | `confirmed` | first crash filed and confirmed in this class |
| R4 | Land `mlir-opt-fuzzer` in `mlir/tools/`, modeled on `llvm-opt-fuzzer`. | @mehdi_amini, asked directly in post 8; answer (post 10): "Looks like a good plan to me! Thanks 🙂"; verbatim in [demand-interviews.md](../research/demand-interviews.md) | `confirmed` | the PR lands in `mlir/tools/` and is accepted upstream |
| R5 | Keep campaign/report infrastructure out of the monorepo. When the target lands, take the automation question to the buildbot/infra side (@infra-area-team). Long-term form: OSS-Fuzz — which today builds zero MLIR targets, so there is no existing channel to conflict with. | @rengolin post 12: "I'd keep it outside of the monorepo. Possibly in the buildbot infra…"; adopted in post 13 bullet 3; verbatim in [demand-interviews.md](../research/demand-interviews.md) (2026-10-31 section) | `confirmed` (placement; exact form open until the infra-area-team discussion) | campaigns run out-of-tree with zero conflict; the infra discussion has been held |

## Design inputs (decided before docs/design/ opens; the design must carry them)

| id | input | why | date |
|----|-------|-----|------|
| D1 | The target's oracle verifies **output**, not just crashes — a pass that finishes but leaves verifier-invalid output is a finding. | MF-007 proved the stakes: on main @ 2026-10-31 the bug is invisible to a crash-only oracle — the pass fails gracefully and only the post-pass verifier reveals it ([BUGLOG](../../triage/BUGLOG.md) addendum 2026-10-31). | 2026-10-31 |
| D2 | The in-tree piece stays **minimal**: one target, parse → `parsePassPipeline` → run → post-pipeline verify (D1 lives here), fatal errors routed to `abort()` so libFuzzer records them. No campaign logic in-tree; infrastructure lives outside the monorepo (R5). | @rengolin post 12; adopted verbatim in post 13 bullets 1/3 — [demand-interviews.md](../research/demand-interviews.md) (2026-10-31 section) | 2026-10-31 |

The pipeline-selection question (input-carried vs process-static
flag) was answered at design opening (2026-11-02): **process-static
flag**, per the llvm-opt-fuzzer precedent and the MF-007 trigger
reduction — see
[design/in-tree-target.md](../design/acceptance-criteria.md#d-1-pipeline-selection-is-a-process-static-flag) (D-1).

## Non-goals

- **Missed-optimization reports.** @nikic: "we should absolutely
  decline to fix it as a default policy."
- **Test-pass crashes.** Collected locally, not filed (@mehdi_amini on
  signal/noise).
- **Fuzzing research.** The research lane is crowded (SYNTHFUZZ,
  FLEX, MLIRSmith, MLIR-Forge, TargetFuzz, MLIRTracer —
  [upstream-terrain.md](../research/upstream-terrain.md)); this project
  lands infrastructure and files bugs.
- **Report volume as a goal.** One motivated issue beats twenty cold
  ones (@banach-space: motivation is the admission criterion).
