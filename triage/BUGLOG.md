# Bug ledger

Append-only record of every issue filed upstream. One row per issue;
update `status`/`fix` in place only after the issue is closed. This is
the project's memory: reproducers get re-verified against `main`
before every follow-up.

Convention: `id` = `MF-NNN`. The upstream issue title must follow the
triage rule — `<Pass/pattern> triggers crash in <actual function>` —
never the low-level assert frame. The issue body must carry a
motivation section (dialect/pass involved and why this input class
matters in practice); reports we cannot motivate are not filed
(@banach-space 2026-10: fuzzer-generated issues without a clear
motivation or practical use case are deprioritized).

| id | date | target / pass-pipeline | root-cause frame | issue link | input class | status | fix |
|----|------|------------------------|------------------|------------|-------------|--------|-----|
| MF-001 | 2026-10-29 | module parse (wasmssa dialect) | SEGV `wasmssa::GlobalOp::parse` → `TypeAttr::get` → null `Type::getContext()` (spike-record §9.4; 10/10 single-process, 10/10 fork `-keep_seed=1`) | — | parser-crash | collected | |
| MF-002 | 2026-10-29 | module parse (wasmssa dialect) | assert `verifyInvariants` — `wasmssa::LocalRefType::get` from `LocalOp::parse`/`inferReturnTypes` | — | parser-crash | collected | |
| MF-003 | 2026-10-29 | module parse (linalg dialect) | assert `attributes may never be null` — `linalg::ReduceOp::parse` → `NamedAttrList::set` | — | parser-crash | collected | |
| MF-004 | 2026-10-29 | module parse (AsmParser) | assert `consumeToken` EOF, `AsmParser/Parser.h:121` | — | parser-crash | collected | |
| MF-005 | 2026-10-29 | module parse (AsmParser) | assert "consumed an unexpected token" | — | parser-crash | collected | |
| MF-006 | 2026-10-29 | `sccp,symbol-dce` | assert `zip_equal` — `dataflow::AbstractSparseForwardDataFlowAnalysis::visitCallOperation` from `SCCP::runOnOperation` | — | valid-ir | collected | |
| MF-007 | 2026-10-29 | `symbol-privatize,remove-dead-values,cse` | assert `value` — `Operation::fold` → `constant_op_binder` from `GreedyPatternRewriteDriver` | — | valid-ir | collected | |

Statuses: `collected` (spike/pre-R4: reproduced & archived, not filed)
→ `filed` → `confirmed` / `needs-info` / `wontfix` → `fixed`.
`input class`: `valid-ir` / `verifier-rejected` / `parser-crash` (only
`valid-ir` gets filed by default; `verifier-rejected` crashes are
collected but batch-reported only if a maintainer asks; `parser-crash`
crashes happen on inputs that never reach a pass pipeline — archived
as robustness material, not filed under the C3 mechanics).
Representative artifacts for the rows above are archived in-repo at
`triage/artifacts/MF-NNN-crash-<sha1>` (filename sha1 = content sha1,
integrity-checkable; full raw set including non-deterministic
artifacts: `~/mlir-fuzz-spike/artifacts/`, outside the repo).
Provenance pairing: `MF-NNN-origin-<basename>.mlir` is the frozen
snapshot of the pre-mutation `mlir/test` source the crash input was
derived from (mutation-diff attribution baseline; the llvm checkout
drifts, so only this snapshot is a stable control). All seven rows
paired (attribution by distinctive tokens + line-overlap, checkout
bd00c2fafc28): MF-001 Conversion/RaiseWasm/wasm-global-set-to-memref.mlir,
MF-002 Conversion/RaiseWasm/wasm-loop-to-cf.mlir,
MF-003 Dialect/Linalg/pad-neutral.mlir,
MF-004 Conversion/ArithToSPIRV/arith-to-spirv-le-specific.mlir
(heavy mutation — 27/78 lines survive; token-based attribution, to be
re-confirmed at minimization),
MF-005 Dialect/ArmSVE/roundtrip.mlir,
MF-006 mlir-runner/async-func.mlir,
MF-007 Conversion/OpenACCToLLVM/data.mlir.
MF-006/MF-007 note (corrected 2026-10-29, supersedes the earlier
"pipeline mutation" reading): the crash inputs are byte-identical to
the prepared seeds — module bodies AND pipeline lines carry no
mutation at all. The mechanically assigned (pipeline, module) pair
crashes as-is: pass selection alone (sccp,symbol-dce /
symbol-privatize,remove-dead-values,cse) drives valid IR into the
buggy pass code. Control experiment: same module under
cse,canonicalize runs clean (rc=0) and under the assigned pipeline
crashes (rc=77). Admission never executes pipelines, so these pairs
were first exercised in the campaign.
