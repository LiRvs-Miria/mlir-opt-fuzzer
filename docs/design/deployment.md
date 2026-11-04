# Deployment shape — what runs where

Genre: design. Derives from requirements (R2–R5, D1, D2, D-1), the
tech survey (spike verdicts, campaign environment facts), and the
prototype walk. This document fixes the deployment topology: which
piece lives where, which build serves which job, and how a crash
becomes a filed issue. Status: draft for review (2026-11-04).

## 1. The three pieces and their homes

| piece | home | boundary |
|---|---|---|
| the fuzz target | llvm/llvm-project, `mlir/tools/mlir-opt-fuzzer/` (a PR) | R4; the community builds it via `add_llvm_fuzzer` (AC-1) |
| campaign + report tooling | this repository | R5: never the monorepo (AC-9); runs wherever a checkout and an MLIR build exist |
| the acceptance net | this repository, [driver/](../../driver/) | verification instrument for the target; not PR material |

Private process records live outside both and are never load-bearing
for this document.

## 2. The in-tree piece (the PR)

Minimal face (D2): parse → pipeline → run → post-pipeline verify →
abort. No corpus, no stats, no reporting (AC-9). One target + build
wiring, nothing else.

**Pipeline channel: `--pipeline=<slug>` over a closed vocabulary.**
Target flags start after libFuzzer's `-ignore_remaining_args=1`
marker (the `FuzzerCLI.h` `parseFuzzerCLOpts` boundary — libFuzzer's
arguments end, the target's begin); the slug resolves against a
.def-file table (`MlirOptFuzzerPipelines.def`, the compiler-rt
`FuzzerFlags.def` idiom: adding a pipeline is one data row, no code
reading). Deciding evidence:

- the option space is closed by design: D-1 removed the
  combination-perturbation axis (AC-2 absorbs it), and the pass set is
  curated by the whitelist criterion — a new pipeline is a deliberate
  .def row, never input-carried;
- fork-mode shell safety: slug values are parenthesis-free, while raw
  pipeline text is eaten by fork mode's unquoted argv join
  (`FuzzerCommand.h toString()`);
- llvm-opt-fuzzer parses its target flags through the same
  libFuzzer/CL boundary.

Startup: the target validates the slug's text exactly as it will run —
against a module-anchored PassManager. `builtin.module` is a constant
under D-1 and the .def carries inner text only; an entry that
re-anchors it is rejected at startup, because it would nest a second
module level and silently run zero passes. A missing flag, an unknown
slug, or an unparseable entry is a startup error (AC-10).

Growth path: a new pipeline = one .def row (source change, recompile).
The whitelist criterion (selects passes, runner-side, mechanically
re-derivable) and the .def (stores pipeline texts, including curated
compositions such as the MF-007 trigger) are two lists kept in sync;
an unknown slug fails loud at startup and the positive controls catch
drift.

Consequences to carry into [acceptance-criteria.md](acceptance-criteria.md):
AC-10/AC-11 get reworded — the option surface is a closed,
source-defined vocabulary (the shape llvm-opt-fuzzer encodes in its
exec name), distinct from input-dependent admission, which stays
banned.

**Development posture**: work happens on a local branch in the llvm
checkout (origin = personal fork, upstream = llvm). The code reaches
llvm's main only through the PR being merged on GitHub — local main
stays a read-only mirror of upstream (fast-forward only, never carries
local work), and the branch is never merged into it. The branch is
pushed to the fork as the PR source. Keep the branch rebased (not
merged) onto upstream/main: a linear history keeps the PR commit list
to exactly our commits; after a rebase, push with
`--force-with-lease`. The PR diff contains only the target and its
build wiring (AC-9 audit).

## 3. Build matrix

| build | flags | serves |
|---|---|---|
| judge | Release, assertions off (NDEBUG), fuzzer coverage | attribution. MLIR asserts are compiled out, so a recorded abort is one of exactly three things: our post-pipeline verify → `abort()`, a genuine SEGV/UB, or the fatal-error handler (AC-7). The net's contract and AC-6 are defined on this build. |
| discovery | Release, assertions on, fuzzer coverage | campaigns. Internal-invariant asserts fire at the bug site — the widest catch. 6 of 7 ledger rows were found this way. |
| ASAN | deferred | memory-error attribution (spike blind spot). Build it when the first non-reproducing or memory-class cluster demands it. |

Division of labor: campaigns run on the discovery build; every
candidate finding is re-verified on the judge build before filing —
only judge-clean crashes become issues. Assertion-only crashes are
investigated first: real-but-masked or debug-only. Build recipe:
[research/build-toolchain.md](../research/build-toolchain.md) Q1 (two
build directories from one checkout).

Both builds take the `add_llvm_fuzzer` engine channel
(`LLVM_LIB_FUZZING_ENGINE`): the fuzzer runtime links at link time,
instrumentation stays compile-time (`-fsanitize=fuzzer-no-link`). The
`LLVM_USE_SANITIZE_COVERAGE` branch is unusable on current ToT — it
injects a compile-time `-fsanitize=fuzzer` that collides with the
default-on PCH (verified 2026-11-04: every fuzzer target fails to
compile, including the upstream parser fuzzers). This is also the
standing answer if reviewers ask why the target is not gated on
sanitize-coverage.

## 4. Corpus, whitelist, positive controls

- **Seeds**: derived from `mlir/test` (public, C1-legal) by script;
  raw corpora stay out of the repository.
- **Pass whitelist**: mechanical criterion (test-file coverage ≥ 3,
  spike verdict), re-derivable by script; runner-side; selects which
  slugs a campaign enumerates.
- **Positive controls**: known-issue reproducers fired at campaign
  start. A control that stops firing means either the upstream fix
  landed or the rig broke — both must be noticed. Initial set:
  `MF-007-min-private` × `remove-dead-values` (rides
  [#237126](https://github.com/llvm/llvm-project/issues/237126);
  re-validate when it is fixed) plus the filed trigger composition.
  (Retires the spike's open item "positive-control set before the
  next campaign".)

## 5. Campaign → report flow

1. **run** — per slug: launch under `-fork=1 -keep_seed=1` on the
   discovery build, writable corpus, artifacts per pipeline.
2. **triage** — replay artifacts single-process on the judge build,
   cluster by (pipeline, error signature), record the reproduction
   rate per cluster. Non-reproducing clusters stay local (R2): heap
   corruption from an earlier input can kill a later one — the
   artifact records the dying input, not the killer; attribution
   tool = the ASAN build, when it exists.
3. **judge re-verification** — §3.
4. **ledger** — [BUGLOG](../../triage/BUGLOG.md) rows (append-only),
   artifacts archived under content-sha1 names.
5. **file** — human motivation gate (R2), then the C3 mechanics.

## 6. Net lifecycle

- **Pre-PR**: acceptance gate — probe rows green plus design-principle
  review = PR-ready.
- **Post-merge**: the net is the *behavioral* red line — the probe
  rows (input contract, oracle firing) guard future target changes.
  The design-principle rows stay review-verified; no probe automates
  them.
- **Endgame**: reviewers may ask for a minimal in-tree lit test — if
  so, some probes graduate into it and the net shrinks; when target
  changes stop, the net retires.

## 7. Out of scope (deferred)

- OSS-Fuzz / buildbot placement — R5's infra-area-team discussion,
  after the target lands.
- Multi-machine campaign orchestration.
