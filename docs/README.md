# docs/ — document map and process line

The documentation follows the engineering pipeline: **research →
requirements → tech survey → design**. Each stage owns one directory
with exactly one write discipline (discipline follows the **origin**
of the content, not its topic): facts observed outside are append-only;
reasoning produced internally is revisable, with history in git.

| Stage | Path | Origin / discipline | Status (2026-11-02) |
|---|---|---|---|
| Research | [research/](research/) | external + machine-verified facts; **append-only** | demand side complete: interviews, terrain, boundaries, standards, versioning, toolchain |
| Requirements | [requirements/](requirements/) | derived from research; `system.md` is the **derivation root**; module-level files join as modules appear; every item `confirmed`/`hypothesis` with source | R1–R4 `confirmed`; R5 `hypothesis` (deferred until R4 lands) |
| Tech survey | [tech-survey/](tech-survey/) | internal engineering investigation; revisable, promotion-dated | promoted to formal survey 2026-11-02; free-axis verdicts in `spike-report.md`; one axis still OPEN (pipeline-selection encoding → design) |
| Design | [design/](design/) | derives from requirements + tech survey; revisable | opened 2026-11-02: D-1 pipeline-selection resolved (process-static flag); acceptance criteria live ([design/acceptance-criteria.md](design/acceptance-criteria.md)) |

Side channels (not stages): crash ledger
[../triage/BUGLOG.md](../triage/BUGLOG.md) (append-only rows) and
frozen evidence [../triage/artifacts/](../triage/artifacts/).
