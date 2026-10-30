# Spike record — mlir-opt-fuzzer closed loop

Related documents: verdicts in
[reports/2026-10-29-spike-report.md](../reports/2026-10-29-spike-report.md);
crash ledger + reproducer pairs in
[../../triage/BUGLOG.md](../../triage/BUGLOG.md) and
`triage/artifacts/`; build/environment facts in
[environment.md](environment.md).

Sealed record, append-only. This file records and supplements facts;
existing entries are never rewritten — corrections are new dated
sections stating which earlier entry they supersede. It is the
traceability source for the experiment that validates the draft
design decisions (A2 executor shape, measurement protocol) ahead of
the R4 gate, after which the design home is `docs/design/`.

Experiment log:

- **2026-10-29 — protocol pre-registered** (initial section, written
  before any campaign run). Priors table empty by design: filled by
  the user before the first campaign (predict-then-diff discipline).
- **2026-10-29 — protocol amended**: §5 priors withdrawn by user
  decision — this is the design-rationality investigation of a
  serious upstream project, not a learning exercise; its deliverable
  is the report that tests the draft design decisions (§6), so
  predict-then-diff priors do not apply. Supersedes the priors
  clauses of the pre-registration entry above (see §5).
- **2026-10-29 — campaign complete**: results recorded in §9
  (matrix, 1 h campaign, 7 deterministic crash signature classes,
  isolation-layer findings).

## 1. What the spike is

Time-boxed, disposable measurement experiment: minimal A1 harness +
filtered corpus, campaign run on a fixed falsification ladder
(1 h → 4 h → aggressive seeds), producing three number groups
(primary / conditional / degradation) that feed specific design
decisions. No PRs, no issue reports; the harness is throwaway.

## 2. Prerequisites (checked off as they land)

- [x] Build resume: `ninja -C ~/mlir-fuzz-build mlir-opt mlir-reduce
      -j 14` — frozen at 1547 steps as of 2026-10-28; recipe and
      build facts in [environment.md](environment.md) Q1/Q5.
      Done 2026-10-29 (EXIT:0, two shards).
- [x] Corpus preprocessing: `mlir/test` filtered by parse+verify
      admission (seed-quality precondition; byte-level mutation of
      MLIR text is expected to have low valid rates). Done
      2026-10-29: 2166/3163 admitted (68.5%).
- [x] Positive control: from known MLIR issues, take ToT-reproducible
      crashers; rerun each 10× single-process, take the first that is
      10/10; that input must then reproduce 10/10 under `-fork=1`.
      Failure = isolation is broken; fix before any campaign, this
      round's reproduction data void. If no candidate reaches 10/10,
      fall back to post-hoc calibration with the campaign's first
      crash (weaker, must be flagged).
      Done 2026-10-29 **with deviation — see §9.1**: no known-issue
      reproducer set was prepared; isolation validated with the
      campaign's own 10/10 deterministic crashes under
      `-fork=1 -keep_seed=1` instead; default fork mode silently
      drops crashing seed inputs (merge-phase behavior).
- [x] Minimal harness (A1 shape, out-of-tree): input = first-line
      pipeline spec + module body; linked via
      `MLIR_DIR=~/mlir-fuzz-build/lib/cmake/mlir`
      (environment.md Q2). Throwaway quality. Done 2026-10-29;
      quirks in §9.5.

## 3. Falsification ladder (fixed order, no in-flight judgment)

1 h → no crash: extend to 4 h → still none: aggressive seeds
(`mlir/test` cases with pipeline length ≥5 or ≥3 dialects) for 1 h.
When the budget fits only one item, prefer extending duration —
same-distribution extra time validates throughput and valid rate
better than switching distribution.

## 4. Measurement protocol (pre-registered 2026-10-29; authoritative
for this experiment)

- **Primary-metric window**: first 100k execs or end of campaign,
  whichever comes first; survival curve bucketed per 10k execs with
  valid count n per bucket; wall-clock recorded as auxiliary only.
- **Dual-axis validity**: module × pipeline recorded separately;
  inputs dying in pipeline construction ("pass requires dialect X",
  missing anchor) are a third input class — dropped by the oracle,
  neither crash nor valid.
- **Conditional metrics** (only with crashes): deterministic crashes
  (single-process 10/10) must reach ≥8/10 under `-fork=1`;
  non-deterministic ones are reported as a fork/single-process ratio
  pair (no preset threshold; anchor = that bug's own single-process
  baseline). Double-vacancy corner (no crash across the whole ladder
  and no 10/10 known issue): reproduction rate untested this round;
  degradation decision on primary metrics only; recorded as an open
  question.
- **Degradation criterion (A2 vs B2)**: compared only if B2 (AFL++
  instrumented mlir-opt) fits the spike budget — same input format,
  same seeds, same valid-rate window rule on both sides. Metrics:
  effective crashes per hour (raw count of crashes triggered during
  pipeline execution on verifier-passing inputs, including crashes
  inside pass and verifier code, excluding parser crashes on invalid
  input; undeduplicated, flagged as such) + valid rate; tie at zero
  breaks toward A2. Coverage: no absolute cross-tool comparison;
  criterion = increments of the last three usable 10k buckets all > 0
  (under 20k total execs: last usable bucket > 0, low confidence
  flagged). If B2 exceeds budget: no degradation decision this round,
  explicitly deferred until a B2 baseline exists.

## 5. Priors — withdrawn 2026-10-29 (supersedes original §5)

User decision 2026-10-29: no priors. The spike is part of the
design-rationality investigation — its deliverable is the report
evidencing the design's soundness — so predict-then-diff priors are
out of scope. The originally pre-registered (empty) priors table is
withdrawn before any campaign ran. Number → decision traceability
lives in §6; measured results land in dated sections (§9 onward).

## 6. Number → decision commitments

Pre-registered so post-hoc rationalization is impossible: every open
design question maps to a measurement in this record.

| Measurement | Feeds which decision |
|---|---|
| module-axis survival curve (rising/flat) | whether a custom mutator is needed (seed-quality decision) |
| whitelist N=3/5 sensitivity (passes obtained) | pass-whitelist admission threshold |
| exec/s × pipeline-length matrix (2/5/10) | pipeline-length distribution shape |
| crash reproduction rate (conditional) | A2 isolation credibility (`-fork=1`) |
| A2 vs B2 same-dimension comparison (optional) | degradation-criterion data |

## 7. Outputs and crash handling

- Results are appended to this file as dated sections (§9 onward);
  raw campaign artifacts (corpus stats, libFuzzer logs) referenced by
  path.
- Crashes during the spike are measured for reproduction rate and
  archived as C3-format material, **not filed** (filing requires full
  C3 mechanics and comes after R4); genuinely new bugs enter
  `triage/BUGLOG.md` (MF-NNN), with `filed` status gated on R4.

## 8. Boundaries

- Before the R4 maintainer signal: harness stays out of tree; no
  spike data on discourse or in issues; no crash reports.

## 9. 2026-10-29 — campaign results (single run, ToT checkout)

Prerequisites met the same day: build finished (`ninja mlir-opt
mlir-reduce` EXIT:0 after two shards from the 1547-step freeze);
corpus admission filtered `mlir/test` (2166/3163 admitted, 68.5% —
rejected files are negative tests, flag-requiring, and malformed
units); minimal A1 harness built out-of-tree against
`~/mlir-fuzz-build` (throwaway; env knobs `MLIR_FUZZ_FIXED_PIPELINE`,
`MLIR_FUZZ_STATS`). Raw artifacts: `~/mlir-fuzz-spike/`
(`corpus/`, `corpus-seeded/`, `corpus-aggressive/`, `artifacts/`,
`logs/`, `harness/`). ToT state: build dir `~/mlir-fuzz-build`,
Release + assertions ON + `-fsanitize=fuzzer`, **no ASAN** — the
crash oracle is signals / assertions / UBSan-reported SEGV, not
heap-error reports.

### 9.1 Positive control — deviation, flagged

The pre-registered control (known-issue crasher, 10/10 single, then
10/10 under `-fork=1`) was **not executed as specified**: no
known-issue reproducer set was prepared. Isolation was validated with
the campaign's own deterministic crashes instead (§9.4) — weaker than
pre-registered, flagged per the fallback clause. One isolation-layer
fact surfaced that the pre-registered control could not have caught:
**default `-fork=1` silently drops crashing seed inputs** — the
parent's feature-collection merge child dies executing the crasher
and the input is excluded from the seed list ("0 seed inputs"; seeds
recovered 10/10 only with `-keep_seed=1`). Crash *detection* during
fork fuzzing is unaffected (artifacts written, jobs counted), but
seed-inclusion filters crashers by default.

### 9.2 exec/s × pipeline-length matrix (fork=1, 300 s each, fixed
pipeline override, same 2166-seed corpus)

| pipeline len | harness execs | module-invalid | ran (survived) | ran rate | tail exec/s |
|---|---|---|---|---|---|
| 2 | 26 689 | 22 775 | 3 906 | 14.6% | ~138 |
| 5 | 40 710 | 37 226 | 3 481 | 8.5% | ~150 |
| 10 | 17 730 | 16 798 | 932 | 5.3% | ~103–148 |

- Module-axis validity does not depend on pipeline length by
  construction; the spread above reflects corpus-evolution drift
  between runs (libFuzzer keeps parser-coverage units regardless of
  module validity — 85–95% of execs die at parse in every config).
- Harness execs > libFuzzer counters: merge children also execute
  inputs (counted in `MLIR_FUZZ_STATS`, not in libFuzzer exec/s).
- Wall-clock exec/s ≈ 103–150 (fork=1, batch overhead included).

### 9.3 Campaign (1 h, fork=1, six 540 s shards, persistent corpus)

- 244 878 harness execs (~54.6 min fuzzing + per-shard corpus load);
  libFuzzer cov 208 900, corpus 10 443 units; per-slice exec/s
  114–168.
- Class breakdown: malformed 56 (0.02%), pipeline-invalid 6 470
  (2.6%), module-invalid 227 804 (93.0%), ran 10 548 (4.3%).
- Survival curve (cumulative ran-rate per 10k-exec bucket): 6.7% →
  5.8% → 4.6% → … → flat 4.3–4.4% from bucket 3 onward (n ≈ 450/10k
  bucket at plateau). The curve **decays then flattens**; corpus
  retention does not lift valid survival under byte mutation.
- Ladder stop: crashes occurred within the first hour
  (per-slice `oom/timeout/crash` counters total 8 crash jobs), so the
  fixed-order ladder **stops at stage 1** — the 4 h extension and the
  aggressive-seed round are not reached (they trigger only on the
  no-crash branch). Aggressive subset (213 seeded files, pipeline
  len 5–8) was prepared but not consumed this round.
- B2 (AFL++ instrumented mlir-opt): not built — exceeds the spike
  budget; **degradation decision explicitly deferred** until a B2
  baseline exists (per §4).

### 9.4 Crashes: 25 artifacts → 7 deterministic signature classes

Reproduction measured per §4: single-process 10×; fork reproduction
under `-fork=1 -keep_seed=1` 10× (see §9.1 caveat for default fork
mode). All 7 classes: **10/10 single-process, 10/10 fork**. 12
further artifacts are non-deterministic (0/10 on immediate single-
process replay; anchor = the campaign crash event itself; fork/single
ratio not measurable this round).

| # | signature (root frame) | pass/pipeline at crash | input class |
|---|---|---|---|
| MF-001 | SEGV `wasmssa::GlobalOp::parse` → `TypeAttr::get` → null `Type::getContext()` | module parse | parser-crash |
| MF-002 | assert `verifyInvariants` — `wasmssa::LocalRefType::get` from `LocalOp::parse`/`inferReturnTypes` | module parse | parser-crash |
| MF-003 | assert `attributes may never be null` — `linalg::ReduceOp::parse` → `NamedAttrList::set` | module parse | parser-crash |
| MF-004 | assert `consumeToken` EOF (`AsmParser/Parser.h:121`) | module parse | parser-crash |
| MF-005 | assert "consumed an unexpected token" (AsmParser) | module parse | parser-crash |
| MF-006 | assert `zip_equal` — `dataflow::AbstractSparseForwardDataFlowAnalysis::visitCallOperation` from `SCCP::runOnOperation` | `sccp,symbol-dce` | valid-ir |
| MF-007 | assert `value` — `Operation::fold` → `constant_op_binder` from `GreedyPatternRewriteDriver` | `symbol-privatize,remove-dead-values,cse` | valid-ir |

MF-006/MF-007 are crashes on inputs that **passed parse+verify**
(pipelines run only after successful admission) — the R3 target
class. MF-001…005 are parser crashes on inputs that do not parse
(collected, not filing candidates under implementation-boundaries).
Representative artifacts: `~/mlir-fuzz-spike/artifacts/crash-*`
(in-repo archive: `triage/artifacts/MF-NNN-crash-<sha1>`, one per
signature class); distinct representatives archived in BUGLOG
(MF-001…MF-007), `filed` gated on R4 per §7.

### 9.5 Harness quirks that affect interpretation

- libFuzzer resolves only the uppercase `LLVMFuzzerInitialize`; a
  lowercase `llvmFuzzerInitialize` is never called (first harness
  build silently skipped pass registration; found via
  "does not refer to a registered pass").
- Pass registration statics in static archives need the
  `MLIRRegisterAll{Dialects,Extensions,Passes}` libs on the link
  line; `registerAllExtensions` is required for transform-dialect
  IR to parse (mlir-opt does the same).
- `-runs` counts seed executions in single-process mode: with N seeds
  and `-runs=M < N`, zero mutation budget remains (first matrix run
  mutated nothing).
- `MLIR_FUZZ_FIXED_PIPELINE` mode still strips line 1 of the input
  (modules never carry the seed's pipeline line).
- The stats hook is an `atexit` handler; libFuzzer's crash exit path
  uses `_Exit`, so any batch that ends in a crash leaves **no**
  summary line — campaign/matrix totals slightly undercount the
  execs that ran inside crash-ending batches.

### 9.6 Threats to validity (facts, for the report consumer)

- No ASAN: memory-error crashes that assertions/SEGV do not catch are
  invisible this round.
- Crash-oracle sensitivity includes assertion builds (assertions ON)
  — assertion crashes are not necessarily UB, but they are
  libFuzzer-visible and match the in-tree fuzzer's oracle.
- Campaign = six 540 s shards sharing one persistent corpus dir
  (per-slice fork startup — seed merge over the whole corpus — cost
  ≈1–2.5 min and grows with corpus size; same-day correction of the
  earlier ~1–2% estimate, which undercounted; see environment.md
  addendum 2026-10-29).
- Validity counts are per-process summaries flushed at worker exit;
  bucket boundaries are approximate at batch granularity (fork=1
  batches ~2k execs).
- Single run, single machine, fixed seed set (43–48); no repetition
  variance measured this round.

## 10. 2026-10-29 — whitelist N=3/5 sensitivity (static scan,
## supplementary to §9)

Method (mechanical, reproducible): extract `--token` flag invocations
from every `mlir/test` `.mlir` file (single awk pass, per-file
dedup), count files per token, keep tokens that parse as registered
pass names in this ToT build (`--pass-pipeline="builtin.module(NAME)"`
per token; the build has tests disabled, so test-only passes are
excluded by construction, matching production mlir-opt). Raw counts:
`~/mlir-fuzz-spike/logs/whitelist-filecounts.txt`.

| criterion | passes admitted |
|---|---|
| ≥1 test file | 140 |
| ≥3 test files | 56 |
| ≥5 test files | 38 |

Caveat: counts flag invocations in test files (comments included),
not curated pipeline usage — bounds popularity, does not rank
usefulness. Feeds the admission-threshold decision (§6 row 2);
verdict in the report (V4).
