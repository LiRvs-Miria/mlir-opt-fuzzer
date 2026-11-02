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
| MF-001 | 2026-10-29 | module parse (wasmssa dialect) | SEGV `wasmssa::GlobalOp::parse` → `TypeAttr::get` → null `Type::getContext()` (spike-record §3.4; 10/10 single-process, 10/10 fork `-keep_seed=1`) | — | parser-crash | collected | |
| MF-002 | 2026-10-29 | module parse (wasmssa dialect) | assert `verifyInvariants` — `wasmssa::LocalRefType::get` from `LocalOp::parse`/`inferReturnTypes` | — | parser-crash | collected | |
| MF-003 | 2026-10-29 | module parse (linalg dialect) | assert `attributes may never be null` — `linalg::ReduceOp::parse` → `NamedAttrList::set` | — | parser-crash | collected | |
| MF-004 | 2026-10-29 | module parse (AsmParser) | assert `consumeToken` EOF, `AsmParser/Parser.h:121` | — | parser-crash | collected | |
| MF-005 | 2026-10-29 | module parse (AsmParser) | assert "consumed an unexpected token" | — | parser-crash | collected | |
| MF-006 | 2026-10-29 | `sccp,symbol-dce` | assert `zip_equal` — `dataflow::AbstractSparseForwardDataFlowAnalysis::visitCallOperation` from `SCCP::runOnOperation` | [#226008 (dup; independent repro commented 2026-10-30)](https://github.com/llvm/llvm-project/issues/226008#issuecomment-6517598757) | valid-ir | collected | |
| MF-007 | 2026-10-29 | `symbol-privatize,remove-dead-values,cse` | assert `value` — `Operation::fold` → `constant_op_binder` from `GreedyPatternRewriteDriver` | [#237126](https://github.com/llvm/llvm-project/issues/237126) | valid-ir | filed | |

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

2026-10-30 re-verification (main @ ee28ae7685e567d56e9ebb15ac4daf451d43f998,
Release + assertions ON, local build): both classes still crash on current main.
- MF-006: confirmed **duplicate of open #226008** (identical zip_equal frame in
  visitCallOperation; fix in flight as PR #226086). Independent minimized repro
  archived as `MF-006-min-f5a666f67a42cfbf7101237d58c08c3884f27861.mlir`
  (9 lines: async.func + call chain — a distinct trigger construct from
  #226008's async.execute region). Action: post the repro under #226008 /
  #226086 (validates fix generality), per gate amendment 2026-10-30 (valid-ir
  reports decoupled from R4 — see AGENTS.md). No new issue, no competing PR.
- MF-007: **NOT covered by the 2026-10-12 fixes** that closed #203226 /
  #206920 (same Matchers.h:491 constant_op_binder assert location) — still
  crashes on main. Minimized to `MF-007-min-c589551684301db8f78b8aebb0572f9803854169.mlir`
  (10 lines: acc.map_info + acc.data on !llvm.ptr values). Minimal trigger
  pipeline: `symbol-privatize,remove-dead-values` — **order-sensitive**; cse
  (in the discovery pipeline) is not needed, every single pass and all other
  orderings run clean. Filing candidate per the gate amendment; issue draft in
  private workspace `work/upstream-filings/`.

2026-10-31 addendum (trigger isolation, main @ 2026-10-31 HEAD, Release
+ assertions ON, local build; reproducible from the artifacts already in
`triage/artifacts/`):

- **Trigger is fully serializable in IR text**: changing
  `func.func @data_if` to `func.func private @data_if` in
  `MF-007-min-*.mlir` and running `remove-dead-values` as the ONLY pass
  reproduces the failure (`expect data entry/exit operation or
  acc.getdeviceptr as defining op` at the `acc.data`).
  `symbol-privatize` is not needed at all — its entire contribution is
  writing `private` into the IR. The failure is a single-IR-perturbation
  property, not a pipeline-composition property; the pass-order axis is
  irrelevant to reachability. Same failure reproduces via the
  privatized mid-state fed to `remove-dead-values` alone (identical
  error text), and on the raw MF-007 artifact body.
- **Form drift between builds, unattributed**: on `ee28ae76`
  (2026-10-30) the same input + pipeline aborts at `Matchers.h:491`
  (the filed form); on main @ 2026-10-31 the pass runs to completion
  and the **post-pass verifier rejects the output** (graceful rc=1,
  same acc.data location). No commits touched
  `RemoveDeadValues.cpp` / `SymbolPrivatize.cpp` / OpenACC IR in the
  window; the assert machinery is confirmed compiled in on the
  2026-10-31 build. The root-cause lldb session must run on a build
  that still asserts (ee28 or a bisect point).
- **Oracle consequence**: on main @ 2026-10-31 this bug is invisible
  to a crash-only oracle — `pm.run` signals failure, is counted as
  `ran`, no crash signal; verified empirically with the spike harness
  (MF-007 A1 input → `ran=1`, rc=0). The only exposure surface is the
  post-pass verifier. Decision recorded as design input D1 in
  [docs/requirements/system.md](../docs/requirements/system.md) (2026-10-31): the
  future in-tree target's oracle includes output verification.

2026-11-02 addendum (asserting-build confirmation, odot machine,
main @ ee28ae76 2026-10-30, Release + assertions ON, local build):

- The single-keyword + single-pass trigger form was confirmed on the
  asserting build for the first time (the 2026-10-31 P1 run only
  covered the non-asserting newer build, where the same input/pipeline
  degrades to the rc=1 verify form). `min` with `func.func @data_if`
  hand-edited to `func.func private @data_if`, fed to
  `remove-dead-values` as the ONLY pass: **rc=134 SIGABRT at
  Matchers.h:491** (`constant_op_binder`, assert `value` failed),
  stack `Operation::fold` <- `applyOpPatternsGreedily` <-
  `OpToOpPassAdaptor::runPipeline` — identical to the filed form.
  Negative control (unmodified min + single rdv) runs clean rc=0;
  positive control (min + symbol-privatize,remove-dead-values) still
  SIGABRTs. Working files: `/tmp/opencode/mf007-confirm/` (odot).
- Structural consequence: in the single-pass form symbol-privatize
  never runs in the crashing process, so its in-process state is
  excluded as a cause; its only contribution is the `private`
  visibility in the IR text. The lldb session (runbook §2-§4) proceeds
  on `min-private` + single `remove-dead-values` with suspect A
  (RemoveDeadValues dropping uses and then folding over a dangling
  use) as the primary hypothesis.

2026-11-02 root cause (CONFIRMED):

- **Crash site**: `Operation::fold` constant-probe loop
  (Operation.cpp:657-658) calls `matchPattern` on every operand
  unconditionally; acc.data operand 0 is null →
  `constant_op_binder` assert (Matchers.h:491). (MLIR "fold" here =
  compile-time constant-folding probe, not an FP fold.)
- **Null slot**: acc.data operand 0 — the `if(%arg1)` use; operand 1
  (%0, map_info result) alive.
- **Who nulls it**: RDV dead-argument cleanup — `nonLiveArgs = [0, 1]`
  (both args judged dead); RemoveDeadValues.cpp:653-654 runs
  `getArgument(deadIdx).dropAllUses()` per dead arg, nulling every use
  slot in place — acc.data.op0 (arg1's use) and map_info.op0 (arg0's
  use). `eraseArguments` (658) then removes both args;
  arith.constant and acc.map_info are erased outright; acc.data — the
  only op in the driver handoff set — survives with a nulled operand
  slot and is folded by the driver.
- **Root cause**: RDV's cleanup produces an invalid intermediate
  state — a surviving op with null operand slots — and hands it to a
  consumer whose fold/matchPattern contract requires non-null Values.
  Two disciplines coexist in the same pass: dead OPERANDS are
  poisoned (line 582, `setOperand(createPoisonedValue(...))`), while
  dead ARGUMENT uses are nulled in place (line 654) — and the pass's
  own poison-replacement step processed the single operand-list entry
  as a no-op, so no poison was applied. `private` is the
  trigger gate: public functions skip the dead-arg analysis entirely
  (RemoveDeadValues.cpp:278), so their args are never dropped.
- **Verification** (throwaway patch, 2026-11-02): replacing the
  in-place nulling at 653-654 with `replaceAllUsesWith(poison)`
  (mirroring the :582 discipline) removes the SIGABRT on asserting
  builds — the pass instead fails at `acc.data`'s semantic verifier
  (`expect data entry/exit operation or acc.getdeviceptr as defining
  op`), rc=1, identical to the no-assertions observation. Confirms
  the null slots (653-654) as the abort trigger; the deeper issue is
  that acc.data itself survives the cleanup — its dataOperands can
  then never satisfy the acc verifier, poison or not. (Also: RDV's
  own poison-replacement step processed its single operand-list entry
  as a no-op — acc.data's slots never received poison.)
