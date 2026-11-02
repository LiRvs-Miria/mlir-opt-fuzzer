# Spike record — design-decision spike for the pass-pipeline fuzzer

Genre: design research (internal-origin, revisable; history lives in
git). This file was re-written 2026-10-30, when the spike was
re-positioned: it is a **design-decision spike serving only the axes
that engineering precedent cannot settle** — not a design-selection
survey. The original sealed-era version (protocol + campaign log in
append-only form) is preserved in git history at the checkpoint
commit `56713a7`. Relocated to `tech-survey/` and promoted to the
formal technical survey on 2026-11-02 (R4 signal received) — the
promotion changes retention, not the lineage rule; see
[README.md](README.md).

Companion documents: decision layer
[spike-report.md](spike-report.md); crash ledger + provenance pairing
[../../triage/BUGLOG.md](../../triage/BUGLOG.md); in-repo artifacts
[../../triage/artifacts/](../../triage/artifacts/); build/environment
facts [environment.md](environment.md).

## 1. Positioning

**What it is.** A time-boxed, disposable measurement experiment: a
throwaway out-of-tree harness (A1 shape: input = first-line pipeline
spec + module body; linked via `MLIR_DIR`; env knobs
`MLIR_FUZZ_FIXED_PIPELINE`, `MLIR_FUZZ_STATS`) plus a filtered
corpus, run on a fixed falsification ladder. Deliverables: decisions
on the free axes, before-baselines, and a bug harvest. Raw campaign
data: `~/mlir-fuzz-spike/` (`corpus/`, `corpus-seeded/`,
`corpus-aggressive/`, `artifacts/`, `logs/`, `harness/`). ToT state:
checkout `bd00c2fafc28`; build `~/mlir-fuzz-build` (Release +
assertions ON + `-fsanitize=fuzzer`, **no ASAN** — the crash oracle
is signals / assertions / UBSan-reported SEGV).

**What it is not.** A design-selection survey. The macro shape is
settled elsewhere, and this campaign carries no decision information
for it:

| axis | settled by |
|---|---|
| executor family (libFuzzer, `add_llvm_fuzzer`) | in-tree fuzzer conventions — the R4 premise itself |
| input format (MLIR module text; bytecode later) | corpus source (`mlir/test`) + M1 proposal |
| in-tree target / out-of-tree campaign split | M1 proposal |

**Free axes the spike measured** (the axes the two precedent parents
disagree on or do not cover):

1. seed-quality strategy (byte-mutation viability on MLIR text);
2. pipeline-selection encoding (pipeline-in-input vs
   process-static flags);
3. pipeline-length distribution shape;
4. runner-layer isolation behavior.

**Boundaries.** Before the R4 maintainer signal: the harness stays
out of tree. *(Amended 2026-10-30 by user ruling: valid-ir crash
reports are decoupled from the R4 gate — after minimization, dedup,
and re-verification against current main, issues may be filed,
discourse linkage is permitted, and bug-fix PRs are allowed; the
harness itself still waits for R4.)* Crashes found during the spike
are measured for reproduction, archived as C3-format material, and
recorded in [BUGLOG](../../triage/BUGLOG.md) as `MF-NNN`.

## 2. Protocol (pre-registered 2026-10-29)

- **Falsification ladder** (fixed order, no in-flight judgment):
  1 h → no crash: extend to 4 h → still none: aggressive seeds
  (`mlir/test` cases with pipeline length ≥5 or ≥3 dialects) for 1 h.
  When budget fits only one item, prefer extending duration.
- **Primary-metric window**: first 100k execs or end of campaign,
  whichever first; survival curve bucketed per 10k execs with valid
  count n per bucket; wall-clock auxiliary only.
- **Dual-axis validity**: module × pipeline recorded separately;
  inputs dying in pipeline construction are a third input class —
  dropped by the oracle, neither crash nor valid.
- **Conditional metrics** (only with crashes): deterministic crashes
  (single-process 10/10) must reach ≥8/10 under `-fork=1`;
  non-deterministic ones reported as a fork/single ratio pair
  (anchor = that bug's own single-process baseline). Double-vacancy
  corner (no crash anywhere and no 10/10 known issue): reproduction
  rate untested; degradation decided on primary metrics only.
- **Degradation criterion (A2 vs B2)**: compared only if B2
  (AFL++-instrumented mlir-opt) fits the spike budget — same input
  format, same seeds, same valid-rate window; metrics = effective
  crashes per hour (crashes during pipeline execution on
  verifier-passing inputs, excluding parser crashes on invalid
  input; undeduplicated, flagged) + valid rate. Coverage: no absolute
  cross-tool comparison; criterion = increments of the last three
  usable 10k buckets all > 0. If B2 exceeds budget: no degradation
  decision this round, explicitly deferred.
  *(2026-10-30 note: this axis is convention-settled — see §1; the
  pre-registered deferral rule is what kept it from costing budget.)*
- **Protocol history**: the original pre-registration carried an
  empty priors table to be filled before the first campaign
  (predict-then-diff); withdrawn 2026-10-29 by user decision before
  any campaign ran — the spike was framed as design-rationality
  investigation, not a learning exercise. That framing was itself
  revised on 2026-10-30 into the positioning in §1.

## 3. Results (facts)

### 3.1 Prerequisites (all met 2026-10-29)

- Build resumed from the 1547-step freeze: `ninja -C ~/mlir-fuzz-build
  mlir-opt mlir-reduce -j 14`, EXIT:0 after two shards.
- Corpus admission: `mlir/test` filtered by parse+verify →
  **2166/3163 admitted (68.5%)**; rejected files are negative tests,
  flag-requiring, and malformed units.
- Positive control: **deviation, flagged** — no known-issue
  reproducer set was prepared. Isolation was validated with the
  campaign's own deterministic crashes instead (§3.4), per the
  pre-registered fallback clause (weaker, must be flagged). Next
  round must prepare the known-issue set before the campaign.

### 3.2 exec/s × pipeline-length matrix (fork=1, 300 s each, fixed-pipeline override, same 2166-seed corpus)

| pipeline len | harness execs | module-invalid | ran (survived) | ran rate | tail exec/s |
|---|---|---|---|---|---|
| 2 | 26 689 | 22 775 | 3 906 | 14.6% | ~138 |
| 5 | 40 710 | 37 226 | 3 481 | 8.5% | ~150 |
| 10 | 17 730 | 16 798 | 932 | 5.3% | ~103–148 |

- Module-axis validity does not depend on pipeline length by
  construction; the spread reflects corpus-evolution drift between
  runs (libFuzzer keeps parser-coverage units regardless of module
  validity — 85–95% of execs die at parse in every config).
- Harness execs > libFuzzer counters: merge children also execute
  inputs (counted in `MLIR_FUZZ_STATS`, not in libFuzzer exec/s).
- Wall-clock exec/s ≈ 103–150 (fork=1, batch overhead included).

### 3.3 Campaign (1 h, fork=1, six 540 s shards, persistent corpus)

- 244 878 harness execs (~54.6 min fuzzing + per-shard corpus load);
  libFuzzer cov 208 900, corpus 10 443 units; per-slice exec/s
  114–168.
- Class breakdown: malformed 56 (0.02%), pipeline-invalid 6 470
  (2.6%), module-invalid 227 804 (**93.0%**), ran 10 548 (**4.3%**).
- **Survival curve** (cumulative ran-rate per 10k-exec bucket):
  6.7% → 5.8% → 4.6% → … → flat 4.3–4.4% from bucket 3 onward
  (n ≈ 450/10k bucket at plateau). The curve decays then flattens;
  corpus retention does not lift valid survival under byte mutation.
- **Ladder stop**: crashes occurred within the first hour (8 crash
  jobs across six shards) → stop at stage 1; the 4 h extension and
  the aggressive-seed round were not reached (they trigger only on
  the no-crash branch). Aggressive subset (213 seeded files,
  pipeline len 5–8) prepared but not consumed.
- B2 not built — exceeds the spike budget; degradation decision
  explicitly deferred per §2.

### 3.4 Crashes: 25 artifacts → 7 deterministic signature classes

Reproduction per §2: all 7 classes **10/10 single-process, 10/10
under `-fork=1 -keep_seed=1`**. 12 further artifacts are
non-deterministic (0/10 on immediate single-process replay; anchor =
the campaign crash event itself; fork/single ratio not measurable
this round).

| # | signature (root frame) | pass/pipeline at crash | input class |
|---|---|---|---|
| MF-001 | SEGV `wasmssa::GlobalOp::parse` → `TypeAttr::get` → null `Type::getContext()` | module parse | parser-crash |
| MF-002 | assert `verifyInvariants` — `wasmssa::LocalRefType::get` from `LocalOp::parse`/`inferReturnTypes` | module parse | parser-crash |
| MF-003 | assert `attributes may never be null` — `linalg::ReduceOp::parse` → `NamedAttrList::set` | module parse | parser-crash |
| MF-004 | assert `consumeToken` EOF (`AsmParser/Parser.h:121`) | module parse | parser-crash |
| MF-005 | assert "consumed an unexpected token" (AsmParser) | module parse | parser-crash |
| MF-006 | assert `zip_equal` — `dataflow::AbstractSparseForwardDataFlowAnalysis::visitCallOperation` from `SCCP::runOnOperation` | `sccp,symbol-dce` | valid-ir |
| MF-007 | assert `value` — `Operation::fold` → `constant_op_binder` from `GreedyPatternRewriteDriver` | `symbol-privatize,remove-dead-values,cse` | valid-ir |

- MF-006/MF-007 crashed on inputs that **passed parse+verify**
  (pipelines run only after successful admission) — the R3 target
  class; the two filing candidates. MF-001…005 are parser crashes on
  inputs that never reach a pipeline (collected, not filing
  candidates). Representative artifacts in-repo:
  `triage/artifacts/MF-NNN-crash-<sha1>`; provenance pairing
  (frozen pre-mutation `mlir/test` sources) in
  [BUGLOG](../../triage/BUGLOG.md).
- **Isolation finding**: default `-fork=1` **silently drops crashing
  seed inputs** — the parent's feature-collection merge child
  executes each seed, dies on the crasher, and the input is excluded
  from the seed list ("0 seed inputs"); seeds recovered 10/10 only
  with `-keep_seed=1`. Crash *detection* during fork fuzzing is
  unaffected (artifacts written, jobs counted).
- Mechanically assigned (pipeline, module) pairs crash as-is:
  pass selection alone drives valid IR into the buggy pass code
  (control: same module under `cse,canonicalize` runs clean rc=0;
  under the assigned pipeline crashes rc=77). Admission never
  executes pipelines, so these pairs were first exercised in the
  campaign.

### 3.5 Pass-whitelist sensitivity (static scan; supplementary)

Method (mechanical, reproducible): extract `--token` flag invocations
from every `mlir/test` `.mlir` file (single awk pass, per-file dedup),
count files per token, keep tokens that parse as registered pass
names in this ToT build (`--pass-pipeline="builtin.module(NAME)"`
per token; the build has tests disabled → test-only passes excluded
by construction, matching production mlir-opt). Raw counts:
`~/mlir-fuzz-spike/logs/whitelist-filecounts.txt`.

| criterion | passes admitted |
|---|---|
| ≥1 test file | 140 |
| ≥3 test files | 56 |
| ≥5 test files | 38 |

Caveat: counts flag invocations in test files (comments included),
not curated pipeline usage — bounds popularity, does not rank
usefulness.

### 3.6 Harness quirks affecting interpretation

- libFuzzer resolves only the uppercase `LLVMFuzzerInitialize`; a
  lowercase `llvmFuzzerInitialize` is never called (first harness
  build silently skipped pass registration; found via "does not
  refer to a registered pass").
- Pass-registration statics in static archives need the
  `MLIRRegisterAll{Dialects,Extensions,Passes}` libs on the link
  line; `registerAllExtensions` is required for transform-dialect IR
  to parse (mlir-opt does the same).
- `-runs` counts seed executions in single-process mode: with N seeds
  and `-runs=M < N`, zero mutation budget remains (first matrix run
  mutated nothing).
- `MLIR_FUZZ_FIXED_PIPELINE` mode still strips line 1 of the input
  (modules never carry the seed's pipeline line).
- The stats hook is an `atexit` handler; libFuzzer's crash exit path
  uses `_Exit`, so any batch ending in a crash leaves **no** summary
  line — campaign/matrix totals slightly undercount execs inside
  crash-ending batches.

### 3.7 Threats to validity

- No ASAN: memory-error crashes that assertions/SEGV do not catch
  are invisible to this oracle.
- Crash-oracle sensitivity includes assertion builds (assertions ON)
  — assertion crashes are not necessarily UB, but they are
  libFuzzer-visible and match the in-tree fuzzer's oracle.
- Six shards shared one persistent corpus dir; per-shard fork startup
  (seed merge over the whole corpus) cost ≈1–2.5 min and grows with
  corpus size (same-day correction of the earlier ~1–2% estimate;
  see environment.md addendum 2026-10-29).
- Validity counts are per-process summaries flushed at worker exit;
  bucket boundaries are approximate at batch granularity (fork=1
  batches ~2k execs).
- Single run, single machine, fixed seed set (43–48); no repetition
  variance this round.

## 4. Decision outcomes (free axes)

| free axis | measurement | decision / status |
|---|---|---|
| seed-quality strategy | survival curve decay + flattening (§3.3) | **byte mutation refuted as-is**; structured `LLVMFuzzerCustomMutator` (parse → structural mutation → print) is a **day-one in-tree component**; the curve is the before-baseline |
| pipeline-selection encoding | MF-006/007 on mechanically assigned (module, pipeline) pairs + control experiment (§3.4) | **OPEN design question** for `docs/design/` (post-R4): pipeline-in-input vs process-static flags; the two precedent parents disagree on this axis; the joint-pairing yield is this campaign's evidence |
| pipeline-length distribution | exec/s matrix, no cliff at 2/5/10 (§3.2) | length distribution shape is a quality choice, not a survival constraint |
| runner-layer isolation | keep_seed finding (§3.4) | runner must run `-keep_seed=1`; the positive-control protocol needs the keep_seed clause |

## 5. Pointers

- Decision layer: [spike-report.md](spike-report.md)
- Crash ledger + provenance pairing:
  [../../triage/BUGLOG.md](../../triage/BUGLOG.md) (MF-001…MF-007,
  `filed` gated on R4)
- In-repo artifacts: [../../triage/artifacts/](../../triage/artifacts/)
- Raw campaign data: `~/mlir-fuzz-spike/`
- Sealed-era original of this file: git history, checkpoint commit
  `56713a7` (before the 2026-10-30 rewrite)
