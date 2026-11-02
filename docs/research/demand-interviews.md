# Demand interviews — verbatim record

Third-party statements grounding this project's requirements. Verbatim
quotes with links and dates; no editorializing in this file — derived
requirements live in [docs/requirements/system.md](../requirements/system.md).
Append-only: new interviews get new sections; existing text is history.

## Thread: [RFC] Guidelines for fuzzer-generated issues (2024-10-15)

<https://discourse.llvm.org/t/rfc-guidelines-for-fuzzer-generated-issues/82556>
— 7 posts total; implementing PR
[#112372](https://github.com/llvm/llvm-project/pull/112372) is open,
draft, unmerged as of 2026-10-28 (last activity 2026-03).

> Fuzzing is a valuable tool for finding compiler bugs, and the LLVM
> project welcomes fuzzer-generated test cases. However, some additional
> guidelines should be followed to make such reports maximally useful.
> — @nikic (RFC body)

> Fuzzer-generated issues should indicate that they are such... Issues
> should include a minimized reproducer (including both the necessary
> code and command line arguments) both as part of the issue description
> and as a godbolt.org link. An effort should be made to deduplicate...
> Reports should always be submitted against current LLVM `main`.
> — @nikic (RFC body)

> Crashes that occur on valid code are more valuable than crashes on
> invalid code... When fuzzing LLVM IR, fatal errors that do not
> generate a stack trace should not be reported. They indicate an
> incorrect use of LLVM, rather than a bug.
> — @nikic (RFC body)

> From the MLIR POV, I'd be in favor of adopting the same general
> guidelines but without some llvm-specific bits like optimization
> levels, fast math, etc…
> — @kuhar (MLIR maintainer)

> These guidelines make sense to me... I think that compiler crashes are
> always a bug, and clearing them out is good for a lot of reasons.
> — @clattner

Prior thread referenced by the RFC: [RFC] Adding a new GH issue tag for
fuzzer-generated issues (2024-06-14),
<https://discourse.llvm.org/t/rfc-adding-a-new-gh-issue-tag-for-fuzzer-generated-issues/79597>

> I have noticed fuzzer generated bugs reports in spurts over time and I
> have generally said we don't really have the bandwidth to deal with a
> large amount of fuzzer generated bugs. Having said that we do welcome
> bugs that our users are likely to run into and will have a high impact
> if fixed... I think maybe we should document our policy on fuzzer
> generated bugs.
> — @shafik (Clang front-end maintainer, in 79597)

> On the LLVM side, for miscompilations or crashes, we'll usually not
> care a lot whether something is fuzzer-generated or not and fix it
> anyway... The main area where I would actively discourage
> fuzzer-generated reports are missed optimizations. If there is no
> evidence that a pattern can also be found in real-world code, then we
> should absolutely decline to fix it as a default policy.
> — @nikic (in 79597)

## Thread: Fuzzing MLIR Infrastructure (2025-02-27)

<https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855>
— xisang0 reports MLIR-infra crashes with low maintainer engagement;
thread contains the success recipe and the triage guidance.

> The problem we have is that a lot of the test passes in MLIR aren't
> designed to be resilient against fuzzing... a lot of the fuzzer
> test-cases are crashes on inputs that so artificial that no one
> consider these really high-priority to fix.
> — @mehdi_amini (MLIR maintainer)

> To be clear: this is not intentional, I consider this a bug actually:
> passes should be conservative and resilient against any input IR!
> However I'm describing the state of things, however sad it is.
> — @mehdi_amini

> We've had a lot of success with fuzzer generated bugs files against
> the SPIR-V dialect and related conversions. These were often, in
> hindsight, relatively simple oversights in our test coverage that the
> fuzzer helped close... You can expect much more engagement from the
> maintainers if you file bugs against load-bearing conversion passes
> that are supposed to be resilient to any valid input IR, and less if
> you target test passes that have some loosely defined set of
> supported inputs... I think that having an official fuzzing guidelines
> like those outlined here [guidelines RFC] would help. We could further
> define mlir-specific considerations.
> — @kuhar (MLIR maintainer)

> Often the crash reports are filled with issues mentioning an assertion
> in a low-level piece of the infra... while actually the relevant
> information for this crash originated from frame 15
> `SimplifyAffineOp<mlir::affine::AffineApplyOp>`... A better description
> could be: `AffineApplyOp canonicalize pattern triggers crash in
> mlir::simplifyAffineMap()`.
> — @mehdi_amini

Filer's own open issues:
<https://github.com/llvm/llvm-project/issues?q=is%3Aissue%20state%3Aopen%20author%3Axisang0>

### 2026-10-30: maintainer response to the in-tree pass-pipeline fuzzer proposal

Post 8 (@LiRvs-Miria, 2026-10-30 01:51 UTC) proposed an in-tree
pass-pipeline fuzzer (`mlir-opt-fuzzer` in `mlir/tools/`, modeled on
`llvm-opt-fuzzer`, seed corpus from `mlir/test`, campaign
infrastructure out-of-tree, C3 reporting discipline) and closed with:
"Question for maintainers: is upstream interested in landing such a
target in-tree, as opposed to it remaining an out-of-tree campaign?"
<https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855/8>

Post 10 (@mehdi_amini, 2026-10-30 09:00 UTC):

> Looks like a good plan to me! Thanks 🙂
> — <https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855/10>

Post 11 (@LiRvs-Miria, 2026-10-30) replies: "Thank you! I'll proceed on
that basis — preparing the in-tree target following the existing
fuzzer-target conventions (the parser fuzzers as the structural
template), with the corpus and campaign tooling staying out-of-tree.
I'll follow up here with the PR, and on the MLIR annex in the
fuzzer-guidelines RFC thread."
<https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855/11>

### 2026-10-31: triager-aggregation model proposed and adopted (posts 12–13)

Post 12 (@rengolin, 2026-10-30) — in reply to post 8:

> "I would like triagers to investigate the report with all results,
> find common patterns and then only create issues for those common
> patterns. So that LLVM developers can look at high-quality issues.
> (maybe that's what you meant?)."
>
> "Current fuzzer issues created in MLIR today are almost entirely
> solved by people with LLMs 'quick fixing' them a couple of hours
> later. This is unsustainable."
>
> "If you mean the infra to run and report, then I'd keep it outside
> of the monorepo. Possibly in the buildbot infra, or some other
> better place to automate. @infra-area-team may have a better idea
> what to do here."
> — <https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855/12>

Post 13 (@LiRvs-Miria, 2026-10-31) adopts the stricter model:

> "Thanks @rengolin — and yes, that's what I meant, though your model
> is stricter than my draft, and I'd like to adopt it.
>
> Concretely, what I'll proceed with:
>
> - **In-tree piece stays minimal**: one target under `mlir/tools/`
>   following the `mlir-parser-fuzzer` conventions (parse →
>   `parsePassPipeline` → run → verify, with the fatal-error handler
>   routed to `abort()` so libFuzzer records it). No campaign logic
>   in-tree.
> - **Reporting defaults to collection, not filing**: out-of-tree
>   tooling clusters results by root-cause frame and involved pass,
>   minimizes each distinct pattern with `mlir-reduce`, dedups against
>   open and historical issues, and files one issue per pattern — only
>   when the pattern can be motivated. Everything else stays in a
>   local ledger. The first hour's results already follow this:
>   #226008 got an independent minimized repro commented on the
>   existing issue rather than a new filing; #237126 was filed as a
>   single distinct pattern.
> - **Run-and-report infra stays out of the monorepo** — I'll take
>   that to @infra-area-team / the buildbot side when the target
>   lands. One relevant fact for that discussion: OSS-Fuzz's llvm
>   project currently builds no MLIR targets at all, so there is no
>   existing auto-filing channel to conflict with.
>
> I'll follow up with the target PR, and with the MLIR annex in the
> fuzzer-guidelines RFC thread."
> — <https://discourse.llvm.org/t/fuzzing-mlir-infrastructure/84855/13>

---

## Thread: fuzzer-generated issue outcomes on the MLIR tracker (2026-10)

Links: github.com/llvm/llvm-project/issues (retrieved 2026-10-29 via
GitHub API; search `repo:llvm/llvm-project`, title contains
`mlir fuzzer`). A systematic single-reporter campaign (Kirito /
Kiritobl), ~32 issues in a two-week window, uniform title discipline
`[mlir][bug][<Pass>][fuzzer-found] <root-cause description>`;
12 closed/completed, 20 open at retrieval time.

> "Folks, I'm sorry, but given how much we're currently struggling
> with review bandwidth in MLIR, I'll be deprioritising
> fuzzer-generated issues unless there's a clear motivation or
> practical use case." — @banach-space (issue 231904, comment
> 2026-10-15)

> "In general, while fuzzing can help uncover genuine bugs, it also
> draws our attention towards corner cases that may never arise in
> practice, and away from real use cases." — @banach-space (231904)

> "...I'd encourage you to focus more on helping us identify the right
> design before proposing fixes. Specifically, in this case: * Does
> unrolling such contractions actually make sense?" — @banach-space
> (231904)

> "However, the number of PRs in this area is increasing significantly,
> and given that both time and the number of available reviewers are
> limited, PRs addressing fuzzer-generated issues might be
> deprioritized." — @FedericoBruzzone (issue 233054, comment
> 2026-10-18)

> "Please add `crash` label and set `Type` to `Bug` for crashes."
> — @EugeneZelenko (issue 233054, comment 2026-10-17)

Report structure exemplar (issue 233054 body): Version (commit hash +
build flags) → Bug Description → Crash Chain & Root Cause → Steps to
Reproduce → minimal Reproducer → Stack Dump.
