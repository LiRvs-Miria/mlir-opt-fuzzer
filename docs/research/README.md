# research/ — two categories, two write disciplines

| Directory | Origin | Discipline |
|---|---|---|
| `demand-research/` | external: upstream terrain, community expectations, toolchain behavior — facts observed outside | **append-only**: facts are recorded and supplemented, never rewritten; corrections are new dated sections superseding the old |
| `design-research/` | internal: investigations serving design decisions (currently the design-decision spike) | **revisable**: rewrites are normal; history lives in git |

The split criterion is the origin of the content, not its topic:
external facts cannot be revised (they are observations); internal
argumentation can (it is reasoning). `requirements.md` derives from
both; `docs/design/` (post-R4) derives from requirements +
design-research.
