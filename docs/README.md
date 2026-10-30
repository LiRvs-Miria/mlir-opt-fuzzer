# docs/ — document map

The repository separates documents by **genre** (each directory is a
rewrite contract), not by topic. One topic — e.g. the 2026-10-29
spike — deliberately spans three of them.

| Path | Genre | Rewrite rule | Contents |
|---|---|---|---|
| `docs/requirements.md` | organizational | revisable, every item `confirmed`/`hypothesis` with source | C1–C3 constraints, R1–R5 requirements |
| `docs/research/*.md` | **sealed facts** | append-only; corrections are new dated sections superseding old ones | environment survey, demand interviews (verbatim maintainer quotes), upstream terrain, spike protocol + measurements |
| `docs/reports/*.md` | judgment | revisable | design-rationality reports (verdicts derived from sealed facts) |
| `docs/design/` | design | starts after the R4 gate | (empty — R4 is `hypothesis`) |
| `../triage/BUGLOG.md` | ledger | append-only rows; `status`/`fix` advance in place | crash classes MF-NNN, filing gated on R4 |
| `../triage/artifacts/` | evidence | frozen | MF-NNN crash reproducers + origin snapshots (pairs) |

Spike (2026-10-29) entry points:
[research/spike-record.md](research/spike-record.md) (protocol +
measurements) →
[reports/2026-10-29-spike-report.md](reports/2026-10-29-spike-report.md)
(verdicts) →
[../triage/BUGLOG.md](../triage/BUGLOG.md) (crashes MF-001…MF-007).
