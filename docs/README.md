# docs/ — document map

The repository separates documents by **genre** (each directory is a
rewrite contract), not by topic. The write discipline follows the
**origin** of the content: facts observed externally are append-only;
reasoning produced internally is revisable, with history in git.

| Path | Genre | Rewrite rule | Contents |
|---|---|---|---|
| `docs/requirements.md` | organizational | revisable; every item `confirmed`/`hypothesis` with source | C1–C3 constraints, R1–R5 requirements |
| `docs/research/demand-research/*.md` | **sealed facts** (external-origin) | append-only; corrections are new dated sections superseding old ones | upstream terrain, demand interviews (verbatim maintainer quotes), implementation boundaries, version management, environment survey, coding standards |
| `docs/research/design-research/*.md` | **design research** (internal-origin) | revisable; history lives in git | design-decision spike: evidence layer (`spike-record`) + decision layer (`spike-report`) |
| `docs/design/` | design | starts after the R4 gate | (empty — R4 is `hypothesis`) |
| `../triage/BUGLOG.md` | ledger | append-only rows; `status`/`fix` advance in place | crash classes MF-NNN, filing gated on R4 |
| `../triage/artifacts/` | evidence | frozen | MF-NNN crash reproducers + origin snapshots (pairs) |

Spike (2026-10-29, re-scoped 2026-10-30) entry points:
[research/design-research/spike-record.md](research/design-research/spike-record.md)
(evidence layer: positioning, protocol, measurements, free-axis
decisions) →
[research/design-research/spike-report.md](research/design-research/spike-report.md)
(decision layer) →
[../triage/BUGLOG.md](../triage/BUGLOG.md) (crashes MF-001…MF-007).
