# Version management survey — upstream branching, releases, backports

Not yet researched. Questions this file must answer before the first
PR; sources listed where known.

## Questions

1. Branch/release model: release branch cut cadence, what lands on
   main vs release, backport (cherry-pick) norms and approval process.
2. PR lifecycle: review requirements (who reviews MLIR PRs), CI
   pipelines (pre-merge/post-merge), commit squash/merge conventions,
   commit message format for mlir/ changes.
3. Fork workflow mechanics: keeping a fork's main synced, branch
   naming conventions seen in accepted contributor PRs.
4. LLVM CLA: signing flow, how the PR check manifests.
5. Issue tracker conventions: labels relevant to us
   (`fuzzer-generated` — does it exist yet per PR #112372?),
   `mlir` issue routing, triage roles.

## Candidate sources

- `llvm/docs/` (ReleaseProcess, CodeReview, DeveloperPolicy,
  GettingInvolved, SourceManagement?)
- llvm-dev / discourse release announcements
- `google/oss-fuzz/projects/llvm/project.yaml` (fuzzing cadence)
- Recent merged `mlir/` PRs as convention exemplars

## Addendum 2026-10-30 — question 4 resolved: no LLVM CLA exists

Source fetched 2026-10-30: LLVM Developer Policy,
https://llvm.org/docs/DeveloperPolicy.html . The current policy
contains no CLA requirement; the question above is void. Verbatim:

Section "Copyright, License, and Patents":

> When you contribute code to the LLVM project, you license it under
> these terms

(the terms being "the Apache-2.0 with LLVM-exception license, which
includes a copyright and patent license").

> The LLVM project does not collect copyright assignments, which
> means that the copyright for the code in the project is held by the
> respective contributors.

Section "Email Addresses" — the requirement that actually applies to
contributors before a first PR:

> the LLVM community requires contributors to have a public email
> address associated with their GitHub commits, so please ensure that
> "Keep my email addresses private" is disabled in your account
> settings. There are many free email forwarding services available
> if you wish to keep your identity private.

Section "Quality" — first-time contributor process note:

> Pull requests should build and pass premerge checks. For
> first-time contributors, this will require an initial cursory
> review to run the checks.

Supersedes question 4 ("LLVM CLA: signing flow, how the PR check
manifests"): there is no CLA and no associated PR check. Historical
context for why the question existed: the CLA requirement was removed
by an LLVM Foundation policy change (2023); not re-verified this
session, recorded as context only.
