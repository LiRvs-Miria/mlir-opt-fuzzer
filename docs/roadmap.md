# Roadmap

Milestones are deliberately small: each is 1–2 weekend blocks. This is
a secondary track in a bandwidth-managed portfolio: upstream
engagement is latency-tolerant, and this line yields to the primary
track whenever both compete for the same block.

## M0 — Scaffold and provenance (done 2026-10-28)

- Repository, license (Apache-2.0 WITH LLVM-exception), scope/IP
  firewall ([ADR-0001](adr/0001-scope-and-ip-firewall.md)).
- Upstream landscape recon archived with full sources:
  [design-notes/2026-10-28-upstream-recon.md](design-notes/2026-10-28-upstream-recon.md)
  — etiquette RFC, the "Fuzzing MLIR Infrastructure" thread (success
  recipe and failure modes), OSS-Fuzz gap evidence, academic prior art
  inventory.

## M1 — Upstream entry (diplomatic, before any code PR)

- Replies in the two existing threads — the
  [fuzzer-guidelines RFC](https://discourse.llvm.org/t/rfc-guidelines-for-fuzzer-generated-issues/82556)
  (offering an MLIR-specific annex) and
  [Fuzzing MLIR Infrastructure](https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855)
  (introducing the in-tree `mlir-opt-fuzzer` plan, referencing kuhar's
  guidelines ask). No new RFC.
- **Accept**: maintainer signal (at least one of mehdi_amini/kuhar
  endorsing the in-tree target direction), archived in design-notes.
- Gate: no PR before this.

## M2 — `mlir-opt-fuzzer` in-tree PR

- Target skeleton modeled on `llvm-opt-fuzzer` (`FuzzMutate`/
  `FuzzerCLI` conventions): MLIR module input, pass-pipeline
  selection, oracle = crash/assert + verifier failure.
- Seed corpus zip from a curated `mlir/test` subset (valid inputs only
  — crashes on valid IR are the valuable kind per the guidelines).
- **Accept**: PR reviewed without a "why do we need this" rejection;
  runs the `mlir/test` corpus cleanly except for found-and-filed bugs.

## M3 — Campaign and triage operations

- Local continuous runs (ASan/UBSan + assertions build).
- Bug ledger live in [triage/](../triage): every report with a
  minimized reproducer, the root-cause frame in the title (per
  mehdi_amini's triage guidance), dedupe check, ToT base,
  `fuzzer-generated` marking, fix tracking.
- Target priority: load-bearing conversion passes first (SPIR-V
  conversions — the proven-fertile class), test passes last (not
  reported).

## M4 — MLIR fuzzing guidelines and corpus maturation

- MLIR-specific fuzzing guidelines document (kuhar's ask) landed under
  `mlir/docs/`.
- Corpus growth loop; stretch: propose OSS-Fuzz integration for the
  MLIR targets.

## Open questions

- Is MLIR-Forge open source or paper-only? (affects prior-art
  citation, not our engineering lane)
- `--list-passes` for mlir-opt: landed or not? (nice-to-have for pass
  enumeration in the fuzzer; the registry API works regardless)
