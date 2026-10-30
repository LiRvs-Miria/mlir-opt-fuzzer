# Spike report — design-rationality measurement for `mlir-opt-fuzzer`

Date: 2026-10-29. Status: pre-R4 evidence document. This report draws
design conclusions from the measurement run recorded in
[spike-record.md](../research/spike-record.md) (sealed archive, §9);
numbers cited there are not repeated in full here. The experiment
protocol was pre-registered before any campaign ran; the measurement
→ decision commitments are in spike-record §6.

## 1. Questions this spike answers

The draft design (A2 executor shape, measurement protocol, seed-quality
strategy, pass-whitelist admission) was built from reasoning plus
literature; none of it had local numbers. The spike was a time-boxed,
disposable experiment to produce exactly the numbers the design
decisions hinge on, before any commitment to an in-tree target (R4 is
still `hypothesis`).

## 2. Verdicts

| # | Design question | Verdict | Decisive evidence |
|---|---|---|---|
| V1 | Is the A2 executor shape (in-process libFuzzer + `-fork=1` isolation) credible for finding and reproducing pass-pipeline crashes? | **Validated** | 8 crash jobs detected and archived in a 1 h campaign; 7 deterministic signature classes, each 10/10 single-process and 10/10 fork reproduction; two of the seven are crashes on verifier-passing IR (the R3 target class) |
| V2 | Does the measurement protocol produce decision-grade numbers within a 1 h budget? | **Validated** | All pre-registered primary metrics landed: exec/s matrix, dual-axis validity, bucketed survival curve, reproduction rates |
| V3 | Is byte-level mutation of MLIR text viable as the seed-quality strategy? | **Refuted as-is** | 93.0% of executions die at module parse; survival rate decays (6.7% → 4.3%) and flattens — corpus retention does not lift valid survival |
| V4 | Pass-whitelist admission threshold (N=3 vs N=5 test-file coverage) | **Measured** | 140 registered pass names invoked in `mlir/test`; 56 pass the N≥3 criterion, 38 the N≥5 criterion |
| V5 | Degradation criterion (A2 vs B2, AFL++ instrumented mlir-opt) | **Deferred** | B2 does not fit the spike budget; per the pre-registered rule the decision is explicitly postponed until a B2 baseline exists |
| V6 | Is crash isolation under `-fork=1` sound? | **Validated with one operational finding** | Default fork mode **silently drops crashing seed inputs** (merge-phase feature collection dies on the crasher; the input is excluded from the seed list). Reproduction requires `-keep_seed=1`. Crash detection during fuzzing is unaffected |

## 3. Evidence per verdict

### V1 — executor shape

The falsification ladder (1 h → 4 h → aggressive seeds) stopped at
stage 1 by its own rule: crashes occurred within the first hour
(8 crash jobs across six shards). 25 crash artifacts reduced to 7
deterministic signature classes (13 artifacts) plus 12
non-deterministic artifacts (0/10 on immediate single-process replay;
anchor = the campaign crash event itself). Signature classes and their
input classes are in `triage/BUGLOG.md` (MF-001…MF-007, status
`collected`, `filed` gated on R4).

The distribution matters for the R3 thesis:

- **MF-006** (`sccp,symbol-dce`) — assertion in
  `dataflow::AbstractSparseForwardDataFlowAnalysis::visitCallOperation`
  reached from `SCCP::runOnOperation`.
- **MF-007** (`symbol-privatize,remove-dead-values,cse`) — assertion in
  `Operation::fold`'s `constant_op_binder` reached from the greedy
  rewrite driver.

Both crashed on inputs that **passed parse and verification** —
pipelines only run after admission succeeds — which is exactly the
"load-bearing conversion passes and core dialects on valid IR" target
class (R3). The other five classes are parser-side crashes on inputs
that never reach a pipeline; they are archived as robustness material,
not filing candidates.

Throughput is adequate for the purpose: ~103–150 exec/s wall-clock at
pipeline lengths 2/5/10 (fork=1, batch overhead included), and the
matrix shows no throughput cliff at longer pipelines — length
distribution shape is a quality choice, not a survival constraint.

### V3 — seed quality (the negative result, and the most consequential one)

Admission filtering of `mlir/test` (2166/3163 files pass parse+verify,
68.5%) is necessary but far from sufficient: during the campaign,
**93.0% of executions die at module parse**, 2.6% at pipeline
construction, and only 4.3% reach `ran` (module parsed + pipeline
executed). The bucketed survival curve decays from 6.7% to 4.3% and
flattens by bucket 3 of 24 (n ≈ 450 valid inputs per 10k-exec bucket at
the plateau — the trend is signal, not noise).

The design implication is direct: the mitigation ladder in the draft
design (round-trip filtering → seed preprocessing → structured
mutator) cannot stop at steps 1–2. Byte mutation keeps feeding the
corpus parser-coverage units that never execute a pass; corpus
retention does not improve valid survival. A structured
`LLVMFuzzerCustomMutator` (parse → structural mutation → print) is the
evidence-backed default assumption for the R4-stage implementation,
with the spike's survival curve as the before-baseline.

### V4 — whitelist sensitivity

Method (mechanical, reproducible): extract `--token` flag invocations
from all `mlir/test` `.mlir` files, deduplicate per file, count files
per token, then keep only tokens that parse as registered pass names
in this ToT build's `mlir-opt` (single awk pass; registration tested
via `--pass-pipeline="builtin.module(NAME)"`). The registration filter
inherently excludes test-only passes (this build has tests disabled,
matching production `mlir-opt`).

| criterion | passes admitted |
|---|---|
| ≥1 test file | 140 |
| ≥3 test files | 56 |
| ≥5 test files | 38 |

The N=3 → N=5 step drops 18 passes (~32%). Both cutoffs produce a
usable whitelist; N=3 is the defensible default (wider dialect
coverage at modest noise cost), with N=5 kept as the conservative
alternative. Caveat: the count measures flag invocations in test files
(including comments), not curated pipeline usages — it bounds
popularity, it does not rank usefulness.

### V6 — isolation

The seven deterministic classes reproduce 10/10 under
`-fork=1 -keep_seed=1`. The `keep_seed` qualifier is the finding: in
default fork mode the parent's feature-collection merge child executes
each seed, dies on a crasher, and the input is silently excluded from
the seed list ("0 seed inputs"). Consequences for the design:

- The runner layer (our tooling around the A2 binary) must run with
  `-keep_seed=1`, or accept that crashing inputs vanish from the
  corpus they were found in.
- Future positive controls cannot rely on default fork mode alone;
  the control protocol needs the `keep_seed` clause.

## 4. Decisions this evidence supports (pre-R4 design layer)

1. **A2 stands.** Coverage feedback + batch isolation + in-tree
   convention are each evidenced; the only competing advantage of B2
   (black-box harness) has no supporting measurement, and the
   degradation comparison is postponed rather than lost.
2. **Seed-quality plan escalates.** Admission filter + seed prep stay
   (they bound the third input class), but the design assumption for
   R4-stage implementation becomes structured mutation, with the
   survival curve here as the before-number.
3. **Whitelist admission: N=3** (56 passes), sensitivity to N=5
   documented; the criterion stays mechanical (test-file coverage),
   re-derivable by script.
4. **Runner-layer requirements grow by one:** `-keep_seed=1`
   (isolation), plus the already-planned artifact handling and
   reproduction-rate measurement.
5. **Ladder discipline confirmed.** The fixed-order ladder stopped the
   campaign at hour 1 on crashes; no budget was spent on the 4 h /
   aggressive-seed branches that only exist for the no-crash path.

## 5. Open items (not covered by this spike)

- B2 baseline for the degradation criterion (deferred per protocol).
- Reproduction ratio for non-deterministic crashes (12 artifacts;
  post-hoc single-process replay was 0/10, so the fork/single pair is
  not measurable this round).
- Single run on one machine with a fixed seed set; no repetition
  variance.
- No ASAN in the build: memory errors that neither assertions nor
  SEGV catch are invisible to this oracle.
- Positive-control deviation: no known-issue reproducer set was
  prepared; isolation was anchored on the campaign's own 10/10
  deterministic crashes instead (weaker, flagged in spike-record
  §9.1). Next round must prepare the known-issue set before the
  campaign.

## 6. Bottom line

One hour of measurement on a throwaway harness produced: two
verifier-passing-IR crash classes in the target category (R3), a
quantified refutation of the byte-mutation seed strategy with the
survival curve as baseline, a mechanical whitelist threshold with
sensitivity data, and one isolation-layer behavior that would have
cost real debugging time had it surfaced after an in-tree landing.
The draft design's load-bearing choices (A2, measurement protocol)
survive contact with data; its weakest point (seed quality) is now a
measured problem with a numbered baseline instead of a literature
concern.

## 7. Postscript 2026-10-30 — re-scoping of the verdicts

Design review (2026-10-30) re-attributes this report's decision
content:

- **V1/V5 were low-information as selection questions.** The R4
  premise (an in-tree target) plus in-tree fuzzer conventions
  (`add_llvm_fuzzer`, libFuzzer) overdetermine the executor-family
  choice; B2 was never a live candidate for an in-tree target. §4
  decision 1 ("A2 stands") cites in-tree convention as evidence —
  the convention, not this campaign, is what settles it.
- The campaign's decision-bearing outputs concentrate on the axes
  convention cannot settle: the seed-quality strategy (V3 — promotes
  the structured custom mutator to a day-one in-tree component),
  the pipeline-selection encoding (pipeline-in-input vs
  process-static flags — the two precedent parents disagree on this
  axis; MF-006/MF-007 are evidence only this campaign produced),
  pipeline-length distribution shape (V2 matrix), and runner-layer
  behavior (V6).
- V4/V6/corpus-retention policy are campaign-layer (out-of-tree
  runner/corpus) decisions; they do not enter the in-tree target.
- The bug harvest (MF-001…MF-007) is a first-class output
  independent of target design.

Future design work (post-R4, `docs/design/`) attributes macro shape
choices to engineering precedent and cites this report only for the
free-axis evidence above.
