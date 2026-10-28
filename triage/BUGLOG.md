# Bug ledger

Append-only record of every issue filed upstream. One row per issue;
update `status`/`fix` in place only after the issue is closed. This is
the project's memory: reproducers get re-verified against `main`
before every follow-up.

Convention: `id` = `MF-NNN`. The upstream issue title must follow the
triage rule — `<Pass/pattern> triggers crash in <actual function>` —
never the low-level assert frame.

| id | date | target / pass-pipeline | root-cause frame | issue link | input class | status | fix |
|----|------|------------------------|------------------|------------|-------------|--------|-----|
|    |      |                        |                  |            |             |        |     |

Statuses: `filed` → `confirmed` / `needs-info` / `wontfix` → `fixed`.
`input class`: `valid-ir` / `verifier-rejected` (only `valid-ir` gets
filed by default; `verifier-rejected` crashes are collected but
batch-reported only if a maintainer asks).
