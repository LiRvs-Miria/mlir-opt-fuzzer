# research/ — demand-side facts, sealed

One directory, one write discipline: everything here is **external or
machine-verified fact**, recorded append-only. Facts are observations
— they are supplemented, never rewritten; corrections are new dated
sections superseding the old ones. Reasoning derived from these facts
lives in [../requirements/](../requirements/) (what to build) and
[../tech-survey/](../tech-survey/) (what we measured).

| File | Contents |
|---|---|
| [demand-interviews.md](demand-interviews.md) | verbatim maintainer statements grounding R1–R4 and the reporting boundaries |
| [upstream-terrain.md](upstream-terrain.md) | verified landscape facts (OSS-Fuzz coverage, in-tree targets) |
| [implementation-boundaries.md](implementation-boundaries.md) | what upstream files/accepts/rejects, with sources (C3 mechanics) |
| [coding-standards.md](coding-standards.md) | LLVM/MLIR code and review conventions (open — needed before the fuzzer target) |
| [version-management.md](version-management.md) | upstream branching, releases, backports (open — needed before the first PR) |
| [build-toolchain.md](build-toolchain.md) | local build/toolchain facts: fuzzer build recipe, `add_llvm_fuzzer` modes, checkout state |

Process line: [research/](.) → [../requirements/](../requirements/) →
[../tech-survey/](../tech-survey/) → [../design/](../design/).
