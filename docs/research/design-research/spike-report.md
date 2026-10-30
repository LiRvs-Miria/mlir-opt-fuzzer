# Spike report — design decisions from the measurement run

Genre: design research (decision layer). Evidence layer:
[spike-record.md](spike-record.md) — protocol, verbatim numbers,
threats to validity live there and are not repeated here.

Original run: 2026-10-29 (1 h campaign, throwaway harness, ToT
checkout `bd00c2fafc28`). This document was re-written 2026-10-30
when the spike was re-positioned — see the lineage rule in §1. The
original framing is preserved in git history (checkpoint commit
`56713a7`).

## 1. Lineage rule

Future design work (post-R4, `docs/design/`) attributes macro shape
choices — executor family, input format, in-tree/out-of-tree split —
to **engineering precedent** (`mlir-parser-fuzzer`, `llvm-opt-fuzzer`,
`add_llvm_fuzzer` conventions), **not to this spike**. The R4 premise
(an in-tree target) already fixes those axes; any measurement spent
"validating" them carries no selection information. This report
covers only the **free axes** the precedent cannot settle.

*(Framing correction, 2026-10-30: the original report carried V1
"executor shape validated" and V5 "A2/B2 degradation deferred" as
verdicts. Both are convention-settled and low-information as
selection questions; they are kept in this traceability note instead
of the verdict table.)*

## 2. Questions answered (free axes only)

1. Is byte-level mutation of MLIR text a viable seed strategy, or
   must the target ship a structured mutator?
2. How should the pass-pipeline selection be encoded — inside the
   fuzzed input (jointly mutated with the module) or as a
   process-static flag (llvm-opt-fuzzer precedent)?
3. Does throughput constrain the pipeline-length distribution?
4. Is crash isolation under `-fork=1` sound, and what does the
   runner layer have to account for?

## 3. Verdicts

| axis | verdict | decisive evidence |
|---|---|---|
| seed-quality strategy | **byte mutation refuted as-is**; a structured `LLVMFuzzerCustomMutator` (parse → structural mutation → print) is a **day-one in-tree component** | 93.0% of executions die at module parse; per-10k-exec survival decays 6.7% → 4.3% and flattens by bucket 3 of 24 — corpus retention does not lift valid survival; admission filtering (2166/3163 admitted) is necessary but far from sufficient |
| pipeline-selection encoding | **OPEN design question** (decision post-R4, `docs/design/`) — evidence now exists | MF-006/MF-007: mechanically assigned (module, pipeline) pairs crash as-is on inputs that passed parse and verification (pass selection alone drives valid IR into buggy pass code; control: same module under `cse,canonicalize` runs clean rc=0, assigned pipeline crashes rc=77). The two precedent parents disagree on this axis; the joint-pairing yield is this campaign's evidence |
| pipeline-length distribution | **no throughput constraint**; distribution shape is a quality choice | exec/s ≈ 103–150 wall-clock at pipeline lengths 2/5/10 (fork=1, batch overhead included); no cliff at longer pipelines |
| runner-layer isolation | **sound, with one operational finding** | 7/7 deterministic classes reproduce 10/10 single-process and 10/10 under `-fork=1 -keep_seed=1`; default fork mode silently drops crashing seed inputs (merge-phase exclusion) — the runner must use `-keep_seed=1`, and positive controls must encode the keep_seed clause |

## 4. Decisions supported

1. **Structured custom mutator, day one.** The mitigation ladder
   cannot stop at round-trip filtering + seed preprocessing; the
   survival curve is the before-baseline for the mutator's effect.
2. **Runner-layer requirements grow by one**: `-keep_seed=1`
   (isolation), plus artifact handling and reproduction-rate
   measurement.
3. **Whitelist admission: N=3** (56 passes), with N=5 (38 passes)
   documented as the conservative alternative; the criterion stays
   mechanical (test-file coverage) and re-derivable by script.
4. **Pipeline-selection encoding enters `docs/design/` as an open
   question with its own evidence base** (MF-006/MF-007 + the joint
   pairing mechanism) instead of a default inherited from
   llvm-opt-fuzzer.
5. **Ladder discipline confirmed.** The fixed-order ladder stopped
   the campaign at hour 1 on crashes; no budget went to the 4 h /
   aggressive-seed branches that only exist for the no-crash path.
   (B2 was correctly deferred by the pre-registered rule — and is
   convention-settled besides.)

## 5. Open items

- B2 baseline for the degradation criterion (deferred per protocol;
  low priority — convention-settled axis).
- Reproduction ratio for non-deterministic crashes (12 artifacts;
  0/10 immediate single-process replay; fork/single pair not
  measurable this round).
- Single run on one machine with a fixed seed set; no repetition
  variance.
- No ASAN in the build: memory errors that neither assertions nor
  SEGV catch are invisible to this oracle.
- **Known-issue positive-control set must be prepared before the
  next campaign** (this round's deviation is flagged in
  spike-record §3.1).

## 6. Bottom line

One hour of measurement on a throwaway harness — scoped to the axes
precedent cannot settle — produced: two valid-ir crash classes in
the R3 target category (the evidence pocket behind the M1 posts), a
quantified refutation of byte-level mutation with the survival curve
as the before-baseline, a mechanical whitelist threshold with
sensitivity data, one isolation-layer behavior that would have cost
real debugging time had it surfaced after an in-tree landing, and
one open macro question (pipeline-selection encoding) that the two
precedent parents cannot answer. The convention-settled axes were
never this campaign's to settle.
