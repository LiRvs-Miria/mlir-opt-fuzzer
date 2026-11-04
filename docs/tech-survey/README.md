# tech-survey/ — the formal technical survey

Internal engineering investigation that grounds design decisions.
Promoted from a disposable spike to the **formal technical survey on
2026-11-02** (R4 maintainer signal received): the design is backed by
a measured investigation, not convention alone. The promotion changes
retention, not the lineage rule — macro shape choices still attribute
to engineering precedent, never to the survey
([spike-report.md §1](spike-report.md)).

## Contents

| File | Role | Discipline |
|---|---|---|
| [spike-record.md](spike-record.md) | evidence layer: positioning, protocol, measurements, threats to validity | revisable (rewrites dated; history in git) |
| [spike-report.md](spike-report.md) | decision layer: free-axis verdicts, decisions supported, open items | revisable |
| [environment.md](environment.md) | campaign-environment facts (fork-mode startup cost, build completion) | append-only addenda |
| [harness/](harness/) | the throwaway A1-shape harness source, versioned 2026-11-02 | frozen snapshot of the survey instrument |

## Out-of-repo pointers

- Raw campaign data (`corpus/`, `corpus-seeded/`, `corpus-aggressive/`,
  `logs/`, bulk `artifacts/`): `~/mlir-fuzz-spike/` — too bulky for
  git; representative crash artifacts live in
  [../../triage/artifacts/](../../triage/artifacts/) with provenance
  pairing in [../../triage/BUGLOG.md](../../triage/BUGLOG.md).
- Harness build instructions: [harness/](harness/) (links the built
  MLIR via `MLIR_DIR`).
